from crewai.tools import BaseTool


class CalculatorTool(BaseTool):
    name: str = "Travel Budget Calculator"
    description: str = (
        "Calculate travel costs including accommodation, food, transport, and activities"
    )

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
