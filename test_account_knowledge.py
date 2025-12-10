#!/usr/bin/env python3
"""
Test script to demonstrate account knowledge integration
"""
from app.prompts_v2 import build_prompt
from app.account_knowledge import get_account_context, format_account_context_for_prompt

print("=" * 80)
print("ACCOUNT KNOWLEDGE INTEGRATION TEST")
print("=" * 80)

# Test 1: Get BMO account context
print("\n1. BMO Account Context:")
print("-" * 80)
bmo_context = get_account_context("BMO")
if bmo_context:
    print(f"Company: {bmo_context['company_name']}")
    print(f"Status: {bmo_context['status']}")
    print(f"Focus: {bmo_context['situation']['focus']}")
    print(f"Working with: {', '.join(bmo_context['team_contacts']['architecture'])}")
    print(f"Key initiatives: {', '.join(bmo_context['key_initiatives'][:3])}")

# Test 2: Get contact-specific context
print("\n2. Contact Context for Lakshmi:")
print("-" * 80)
lakshmi_context = format_account_context_for_prompt("BMO", "Lakshmi")
print(lakshmi_context)

# Test 3: Build prompt with account knowledge
print("\n3. Prompt with Account Knowledge (Lakshmi at BMO):")
print("-" * 80)
system_prompt, user_prompt = build_prompt(
    message_type="executive_alignment",
    prospect_name="Lakshmi",
    prospect_title="SVP Engineering",
    prospect_company="BMO",
    unique_fact="Involved with Hopeworks charity",
    business_initiative="Leading digital transformation",
    manager_name="Sandeep"
)

# Show account knowledge section
if "[ACCOUNT KNOWLEDGE]" in system_prompt:
    start = system_prompt.find("[ACCOUNT KNOWLEDGE]")
    end = system_prompt.find("\n\n", start + 100)
    if end == -1:
        end = len(system_prompt)
    print(system_prompt[start:end])
else:
    print("❌ Account knowledge not found in prompt!")

# Test 4: Build prompt without account knowledge (unknown company)
print("\n4. Prompt without Account Knowledge (Unknown Company):")
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
    print("❌ Should not have account knowledge for unknown company!")
else:
    print("✅ No account knowledge injected (as expected)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
