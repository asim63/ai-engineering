from ollama import chat

def call_llm(prompt):
    stream = chat(
        model = "qwen3:8b",
        messages= [{"role":"user","content":prompt}],
        options={"temperature": 0},
        stream= True,
        think= False,
    )
    full = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        full += piece
    return full

def support_bot_eval(user_query, bot_response, company_policy_snippet):
    prompt = f"""
    You are evaluating a customer support bot response for a SaaS company.
    User query: {user_query}
    Bot_response: {bot_response}
    Relevant company policy: {company_policy_snippet}
    
    
    Score each (1-5), citing evidence:
    1. Policy adherence: Does the response comply with the policy?(Critical- a violation caps this at 1) 
    2. Tone: Professional and empathetic, not robotic or dismissive?
    3. Resolution: Does it actually resolve or clearly progress the user's issue?
    4. No overpromising: Does it avoid comitting to things not guaranteed by policy?
    
    Respond in format:
    Policy adherence: <score> - <evidence>
    Tone: <score> - <evidence>
    Resolution: <score> - <evidence>
    No overpromising: <score> - <evidence>
    """
    return call_llm(prompt)
    
    
company_policy_snippet = """
REFUND & CANCELLATION POLICY (SaaS Subscriptions)

1. Refund eligibility:
   - Full refund available within 14 days of initial purchase, no questions asked.
   - After 14 days, refunds are only issued for verified billing errors (e.g., duplicate charges) or documented service outages exceeding 24 hours.
   - No partial refunds for unused time on annual plans after the 14-day window.

2. Cancellation:
   - Users can cancel anytime from Account Settings > Billing. Cancellation takes effect at the end of the current billing cycle — no immediate termination of access.
   - Cancelling does NOT automatically trigger a refund for the current cycle.

3. Refund processing time:
   - Approved refunds are processed within 5-7 business days to the original payment method.
   - Support agents must NOT promise a specific refund date, only the 5-7 business day window.

4. Escalation rules:
   - Agents cannot approve refunds outside policy on their own authority.
   - Any refund request outside the above criteria must be escalated to a supervisor — the agent must say this explicitly rather than approving or denying it themselves.

5. Tone requirements:
   - Acknowledge the user's frustration before explaining policy.
   - Never blame the user for the situation, even if the request falls outside policy.
"""

# Case 1: Should score well — correct, on-policy, appropriate tone
user_query_1 = "I subscribed 20 days ago and want a full refund, I just don't use it enough."
bot_response_1 = (
    "I completely understand, and I'm sorry it hasn't worked out for you. "
    "Since it's been past our 14-day refund window and this isn't a billing error, "
    "I'm not able to issue a refund directly, but I've escalated this to my supervisor "
    "who will review it and follow up with you shortly."
)

# Case 2: Should get flagged — violates policy (overpromises) and skips escalation
user_query_2 = "I subscribed 20 days ago and want a full refund, I just don't use it enough."
bot_response_2 = (
    "No worries! I've gone ahead and approved your full refund — you'll see the money "
    "back in your account by tomorrow."
)

print(support_bot_eval(user_query_1, bot_response_1, company_policy_snippet))
print("\n---\n")
print(support_bot_eval(user_query_2, bot_response_2, company_policy_snippet))