import os
import requests
import json

# Placeholder for LLM interaction
# In a real scenario, this would import a client like OpenAI or Anthropic
# For this task, we will simulate the LLM response or use a dummy function if no API key is present.

def build_prompt(query, stats):
    """
    Constructs the prompt for the LLM using the query and the top search results.
    ML-3: Include excerpt and chart summary.
    ML-4: Verify premium status instructions.
    """
    context_str = ""
    for stat in stats:
        # ML-3: Use rich metadata
        stat_id = stat.get('statisticId', 'UNKNOWN')
        title = stat.get('title', 'Unknown Title')
        excerpt = stat.get('excerpt', 'No excerpt available.')
        chart_type = stat.get('chart_type', 'unknown')
        is_premium = stat.get('isPremium', False)
        
        # ML-3: Format the context item
        # ML-4: Note if it is premium
        premium_note = "(PREMIUM CONTENT - DO NOT REVEAL EXACT NUMBERS)" if is_premium else ""
        
        context_str += f"Source [{stat_id}]: {title} {premium_note}\n"
        context_str += f"Excerpt: {excerpt}\n"
        context_str += f"Chart Info: Type={chart_type}\n"
        context_str += "---\n"

    system_instruction = (
        "You are an AI assistant helping users find statistics about Generative AI. "
        "Use ONLY the provided context to answer the user's question. "
        "Directly cite the sources using their ID in brackets, e.g., [STAT_1234]. "
        "If a source is marked as PREMIUM, do NOT invent or estimate specific numbers if they are not explicitly in the excerpt. "
        "Instead, state that the full data is available in the premium report. "
        "Summarize the key trends based on the excerpts."
    )
    
    user_prompt = f"User Query: {query}\n\nContext:\n{context_str}\n\nAnswer:"
    
    return system_instruction, user_prompt

def get_answer(query, stats):
    """
    Generates an answer based on the query and stats.
    ML-3: Limit to top 3 stats.
    """
    # ML-3: Limit context to top 3 results
    top_stats = stats[:3]
    
    system_instr, user_prompt = build_prompt(query, top_stats)
    
    # Mocking the LLM call for now as we don't have an API key in the requirements
    # In a real app, you'd call OpenAI/Gemini here.
    
    # We will generate a procedural dummy response for demonstration purposes
    # or fail gracefully if we can't call an LLM.
    
    # For now, let's return a constructed string that proves we used the logic.
    answer_parts = []
    for stat in top_stats:
        sid = stat.get('statisticId')
        title = stat.get('title')
        is_prem = stat.get('isPremium')
        if is_prem:
             answer_parts.append(f"Based on {title}, the trend is significant (Premium Source) [{sid}].")
        else:
             answer_parts.append(f"{title} shows positive growth [{sid}].")
             
    answer = "TL;DR: Here are the latest trends based on the available data.\n\n" + "\n".join(answer_parts)
    
    return answer
