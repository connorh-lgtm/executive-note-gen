#!/usr/bin/env python3
"""
Test script to demonstrate account knowledge integration
"""
from app.prompts_v2 import build_prompt
from app.account_knowledge import get_account_context, format_account_context_for_prompt, list_known_accounts

print("=" * 80)
print("ACCOUNT KNOWLEDGE INTEGRATION TEST")
print("=" * 80)

# Test 1: List known accounts
print("\n1. Known Accounts:")
print("-" * 80)
accounts = list_known_accounts()
print(f"Found {len(accounts)} accounts: {', '.join(sorted(accounts))}")

# Test 2: Get context for first available account
print("\n2. Account Context (first available):")
print("-" * 80)
if accounts:
    first_account = sorted(accounts)[0]
    context = get_account_context(first_account)
    if context:
        print(f"Company: {context['company_name']}")
        print(f"Industry: {context.get('industry', '(not set)')}")
        print(f"Status: {context.get('status', '(not set)') or '(not set)'}")
    else:
        print(f"No context returned for {first_account}")
else:
    print("No accounts found -- populate accounts/*.md files")

# Test 3: Format account context for prompt
print("\n3. Formatted Account Context:")
print("-" * 80)
if accounts:
    formatted = format_account_context_for_prompt(sorted(accounts)[0])
    if formatted:
        print(formatted)
    else:
        print("(empty -- account sections not yet populated)")

# Test 4: Build prompt with account knowledge
print("\n4. Prompt with Account Knowledge:")
print("-" * 80)
if accounts:
    first_account = sorted(accounts)[0]
    context = get_account_context(first_account)
    company_name = context['company_name'] if context else first_account
    system_prompt, user_prompt = build_prompt(
        message_type="executive_alignment",
        prospect_name="Test Contact",
        prospect_title="CTO",
        prospect_company=company_name,
        unique_fact="Recently promoted",
        business_initiative="Digital transformation",
        manager_name="Test Manager"
    )

    if "[ACCOUNT KNOWLEDGE]" in system_prompt:
        start = system_prompt.find("[ACCOUNT KNOWLEDGE]")
        end = system_prompt.find("\n\n", start + 100)
        if end == -1:
            end = len(system_prompt)
        print(system_prompt[start:end])
    else:
        print("Account knowledge not in prompt (sections may not be populated yet)")

# Test 5: Build prompt without account knowledge (unknown company)
print("\n5. Prompt without Account Knowledge (Unknown Company):")
print("-" * 80)
system_prompt2, _ = build_prompt(
    message_type="cold_outreach",
    prospect_name="John Doe",
    prospect_title="CTO",
    prospect_company="Unknown Corp",
    unique_fact="Recently promoted",
    business_initiative="Cloud migration",
    manager_name="Jake"
)

if "[ACCOUNT KNOWLEDGE]" in system_prompt2:
    print("ERROR: Should not have account knowledge for unknown company!")
else:
    print("OK: No account knowledge injected (as expected)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
