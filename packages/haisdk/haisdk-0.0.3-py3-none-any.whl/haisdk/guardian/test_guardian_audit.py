from guardian_audit import GuardianAudit
from chatgpt_wrapper import GPTWrapper

config = {
    "tenant_id": "HolisticAI-58jnt",
    "apikey": "YmIzMGQzZDAtMTY0Yi00Mjk2LWIxY2UtMTJhMWRmMjhhNTI3",
    "audit_id": "069a73c0-dc13-422b-a1df-36143e142dca"
}

audit = GuardianAudit(config)
gpt = GPTWrapper()

audit_prompts = audit.load_prompts()
messages = []
# audit ChatGPT
for prompt in audit_prompts['stereotype_prompts']:
    completion = gpt.complete(prompt)["choices"][0]["text"]
    processed_prompt = prompt.split(":")[1]
    processed_prompt = processed_prompt + completion

    messages.append({
    "prompt": prompt,
    "response": processed_prompt.strip()
    })

# send messages to be processed
audit.process(messages)



