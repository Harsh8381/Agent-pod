from rag.retriever import retrieve_documents
from llm_client import call_llm


class ClinicalDecisionSupportAgent:
    def analyze(self, patient_summary):
        context = retrieve_documents(patient_summary, top_k=5)

        prompt = f"""
Medical Knowledge Base:
{context}

Patient Summary:
{patient_summary}

Return only valid JSON.

Do not include markdown.
Do not include explanation outside JSON.
Do not include ```json.
Do not include triple backticks.

Use this exact JSON structure:

{{
  "possible_diagnosis": "",
  "risk_assessment": "",
  "recommended_tests": "",
  "treatment_suggestions": "",
  "follow_up_plan": ""
}}
"""

        response = call_llm(
            prompt=prompt,
            system_prompt="""
You are a Clinical Decision Support Assistant.
Use only the provided medical knowledge base context and patient summary.
Return valid JSON only.
Do not include markdown.
Do not include triple backticks.
Do not provide a final diagnosis. Provide decision-support suggestions only.
"""
        )

        return response.strip()

    def generate(self, patient_summary):
        return self.analyze(patient_summary)