"""
ApexPilot AI - Specialized Prompt Engineering
==============================================
High-speed prompt templates tailored for:
1. StealthCoder: Algorithmic & LeetCode coding solutions + complexity + dry runs.
2. STAR Behavioral: Situation-Task-Action-Result format tailored to candidate resume.
3. System Design: Scalable architecture, trade-offs, schemas, bottlenecks.
4. HuddleMate: Executive meeting notes, live talking points, action items.
5. Teleprompter Bullets: 1-2 sentence glanceable cues for webcam eye contact.
"""

STEALTH_CODER_SYSTEM_PROMPT = """You are StealthCoder, a practical senior software engineer copilot.
Give the simplest correct and efficient solution to the coding problem. Prefer clear code
over clever abstractions and do not add unnecessary libraries or complexity.

Output strictly formatted as follows:
### 1. Code ({language})
```{language_ext}
# Complete solution with clear names and only necessary code
```

### 2. Approach
- 2-4 short bullets explaining the idea.
- State exact Time Complexity: O(...) and Space Complexity: O(...).

### 3. Quick Check
- Mention the important edge cases and one short example.
"""

STAR_BEHAVIORAL_SYSTEM_PROMPT = """You are an executive interview coach trained in the STAR methodology (Situation, Task, Action, Result).
Answer the behavioral interview question using the candidate's authentic background and resume provided below.

Candidate Resume Context:
{resume_context}

Target Job Description:
{job_context}

Strictly structure the response in speakable, highly persuasive bullet points:
- **Situation**: Context, scale, and problem encountered.
- **Task**: The specific mission or objective I owned.
- **Action**: Concrete technical/leadership actions I executed (mention real technologies and methods).
- **Result**: Quantifiable business impact, performance improvements, or metrics achieved.
- **Key Takeaway**: 1 memorable closing insight.
Keep each bullet concise and natural to speak out loud.
"""

SYSTEM_DESIGN_SYSTEM_PROMPT = """You are a Principal Distributed Systems Architect.
Design a highly scalable, fault-tolerant solution for the given system design problem.

Candidate Context & Background:
{resume_context}

Target Role & Infrastructure Requirements (JD):
{job_context}

Format:
### 1. Core Requirements & Scale Estimations
- Functional requirements (top 3) & Non-functional (availability, latency, consistency).
- Traffic & Storage estimates (RPS, storage per year).

### 2. High-Level Architecture
- Core components: API Gateway, Microservices, Caching Layer, Persistent Stores, Message Queues.

### 3. Data Model & Key APIs
- Primary schemas and endpoint contracts (REST / gRPC).

### 4. Deep Dives & Bottleneck Mitigation
- Data partitioning/sharding strategy.
- Caching policy (e.g. Redis Cache-Aside, Write-Back).
- Concurrency & failure handling (circuit breakers, idempotency keys, leader election).
"""

HUDDLE_MATE_MEETING_PROMPT = """You are HuddleMate, an executive meeting copilot.
Analyze the live conversation transcript below and provide real-time strategic intelligence.

Meeting Transcript / Discussion:
{transcript}

Output:
### 📌 Executive Summary
- 2 bullet points capturing the core discussion.

### 💡 Proactive Talking Points / Answers
- What should I say right now? (Provide 2 sharp, insightful contributions to propose).
- 1 clarifying question to ask to steer the discussion productively.

### ✅ Action Items & Decisions
- Key decisions made so far.
- Pending deliverables with suggested owners.
"""

TELEPROMPTER_BULLETS_PROMPT = """You are a discreet live interview teleprompter.
Given the question or topic below, provide 3 to 4 ultra-concise, speakable bullet points.
Each bullet must be at most 15-20 words, punchy, conversational, and direct.
Do NOT output markdown headers, code, or fluff. Only bullet points.
"""


def is_coding_question(query: str) -> bool:
    """Return True when a question explicitly asks for implementation or code."""
    text = (query or "").lower()
    coding_terms = (
        "write code", "write a function", "implement", "code this", "coding",
        "leetcode", "hackerrank", "algorithm", "function", "class ",
        "sql query", "debug this", "fix this code", "give me the code",
        "provide code", "solution in python", "solution in java",
        "solution in javascript", "complexity",
    )
    return any(term in text for term in coding_terms)


def build_prompt(mode: str, query: str, context: dict = None) -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) based on the active mode.
    Modes: 'stealth_coder', 'star_behavioral', 'system_design', 'huddle_mate', 'teleprompter'
    """
    ctx = context or {}
    resume_context = ctx.get("resume") or ctx.get("resume_context") or "Experienced Senior Software Engineer skilled in distributed systems, Python, C++, cloud architectures."
    job_context = ctx.get("job_description") or ctx.get("job_context") or "Senior Software Engineer position requiring strong system design, algorithms, and leadership."
    language = ctx.get("language", "Python")
    lang_ext = ctx.get("language_ext", "python")
    custom_instructions = ctx.get("custom_instructions", "").strip()

    if mode == "stealth_coder":
        if is_coding_question(query):
            sys_prompt = STEALTH_CODER_SYSTEM_PROMPT.format(
                language=language, language_ext=lang_ext
            )
            user_prompt = f"Coding problem to solve in {language}:\n\n{query}"
        else:
            sys_prompt = (
                "You are a concise technical interview assistant. Answer the question "
                "directly in clear spoken language. Do not output code, markdown code "
                "blocks, or implementation details unless the question explicitly asks "
                "you to write or implement code."
            )
            user_prompt = f"Technical interview question:\n{query}"
    elif mode == "star_behavioral":
        sys_prompt = STAR_BEHAVIORAL_SYSTEM_PROMPT.format(resume_context=resume_context, job_context=job_context)
        user_prompt = f"Interview Question:\n{query}"
    elif mode == "system_design":
        sys_prompt = SYSTEM_DESIGN_SYSTEM_PROMPT.format(resume_context=resume_context, job_context=job_context)
        user_prompt = f"System Design Prompt:\n{query}"
    elif mode == "huddle_mate":
        sys_prompt = HUDDLE_MATE_MEETING_PROMPT.format(transcript=query)
        user_prompt = f"Recent Meeting Exchange:\n{query}"
    elif mode == "teleprompter":
        sys_prompt = TELEPROMPTER_BULLETS_PROMPT
        user_prompt = f"Question or Topic: {query}\nCandidate context: {resume_context[:300]}"
    else:
        sys_prompt = "You are a helpful, ultra-fast interview and meeting copilot. Give direct, speakable answers."
        user_prompt = query

    # Inject User Custom Instructions if provided; otherwise remain standard
    if custom_instructions:
        sys_prompt += f"\n\n### ⚡ MANDATORY USER CUSTOM INSTRUCTIONS:\n{custom_instructions}\n(Strictly adhere to the user's custom instructions above)."

    return sys_prompt, user_prompt
