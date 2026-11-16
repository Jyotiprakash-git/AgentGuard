
import requests

from pydantic import Field
from langchain_core.tools import BaseTool


class AgentGuardTool(BaseTool):

    wrapped_tool: BaseTool = Field(exclude=True)
    agent_api_key: str = Field(exclude=True)

    action: str
    resource: str

    base_url: str = "http://127.0.0.1:8000"

    # --------------------------------------------------
    # COMMON HEADERS
    # --------------------------------------------------

    def _get_headers(self):
        return {
            "X-Agent-API-Key": self.agent_api_key
        }

    # --------------------------------------------------
    # STEP 1: EVALUATE ACTION WITH AGENTGUARD
    # --------------------------------------------------

    def _evaluate_action(self, request_data):

        payload = {
            "action": self.action,
            "resource": self.resource,
            "request_data": request_data
        }

        try:
            response = requests.post(
                f"{self.base_url}/authorization/evaluate",
                json=payload,
                headers=self._get_headers(),
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as exc:

            print("AgentGuard API error:", exc)

            if exc.response is not None:
                print("HTTP status:", exc.response.status_code)
                print("Response:", exc.response.text)

            raise RuntimeError(
                "AgentGuard security check failed. "
                "Tool execution blocked."
            ) from exc

    # --------------------------------------------------
    # STEP 2: CHECK APPROVAL STATUS
    # --------------------------------------------------

    def check_approval_status(self, approval_id):

        try:
            response = requests.get(
                f"{self.base_url}/authorization/"
                f"approval-requests/{approval_id}/status",
                headers=self._get_headers(),
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as exc:

            print("Approval status API error:", exc)

            raise RuntimeError(
                "Could not verify approval status. "
                "Execution blocked."
            ) from exc

    # --------------------------------------------------
    # STEP 3: EXECUTE APPROVED ACTION
    # --------------------------------------------------

    def execute_approved_action(self, approval_id):

        try:
            response = requests.post(
                f"{self.base_url}/authorization/"
                f"execute/{approval_id}",
                headers=self._get_headers(),
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as exc:

            print("Approved execution API error:", exc)

            if exc.response is not None:
                print("HTTP status:", exc.response.status_code)
                print("Response:", exc.response.text)

            raise RuntimeError(
                "Approved action could not be executed."
            ) from exc

    # --------------------------------------------------
    # STEP 4: MAIN LANGCHAIN TOOL EXECUTION
    # --------------------------------------------------

    def _run(self, tool_input: str = "", **kwargs) -> str:

        # Collect actual tool inputs
        if kwargs:
            request_data = dict(kwargs)
        else:
            request_data = {
                "input": tool_input
            }

        request_data["resource"] = self.resource

        # Ask AgentGuard to evaluate the action
        result = self._evaluate_action(request_data)

        decision = result.get("decision")

        # ----------------------------------------------
        # CASE 1: DENY
        # ----------------------------------------------

        if decision == "DENY":

            raise PermissionError(
                "AgentGuard blocked this action."
            )

        # ----------------------------------------------
        # CASE 2: REQUIRE APPROVAL
        # ----------------------------------------------

        if decision == "REQUIRE_APPROVAL":

            approval_id = result.get("approval_request_id")

            raise PermissionError(
                "Human approval required. "
                f"Approval request ID: {approval_id}. "
                "Approve the request and then execute it "
                "through AgentGuard."
            )

        # ----------------------------------------------
        # CASE 3: ALLOW
        # ----------------------------------------------

        if decision == "ALLOW":

            if kwargs:
                return self.wrapped_tool.invoke(kwargs)

            return self.wrapped_tool.invoke(tool_input)

        # ----------------------------------------------
        # UNKNOWN SECURITY DECISION
        # ----------------------------------------------

        raise PermissionError(
            "Unknown security decision. "
            "Execution blocked."
        )
