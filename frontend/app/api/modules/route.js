import { NextResponse } from 'next/server';

export async function POST(req) {
  try {
    const { subject, clusterStats } = await req.json();
    const topic = subject || "Reasoning and Cognitive Learning";

    const apiKey = process.env.DEEPSEEK_API_KEY;
    if (!apiKey) throw new Error("DEEPSEEK_API_KEY not set.");

    const prompt = `You are an expert curriculum designer for the EMERGENCE Adaptive Classroom Intelligence System. Generate 3 precise teaching content modules for the subject: "${topic}".

CLASSROOM DATA:
${clusterStats ? `- Excelling students: ${clusterStats.excelling || 0} (avg score: ${clusterStats.excellingAvg || 'N/A'}%)
- Developing students: ${clusterStats.developing || 0} (avg score: ${clusterStats.developingAvg || 'N/A'}%)
- Struggling students: ${clusterStats.struggling || 0} (avg score: ${clusterStats.strugglingAvg || 'N/A'}%)` : '- Default classroom distribution.'}

Return a JSON object with exactly 3 keys. Each value is a Markdown string.

{
  "excelling": "markdown content here",
  "developing": "markdown content here",
  "struggling": "markdown content here"
}

STRICT CONTENT RULES — FOLLOW EXACTLY:
- Write ONLY the actual teaching content that a faculty member should deliver to students in each cluster.
- Write in detailed, multi-paragraph format. Each module should be 500+ words of REAL content.
- DO NOT include: "Learning Outcomes", "Learning Objectives", "Tips", "Self-Assessment", "Quick Check", "Confidence Booster", "Faculty Note", or any meta-sections about how to teach.
- DO NOT include generic motivational text or filler.
- Focus ONLY on: concept explanations, worked examples, problem-solving strategies, real-world applications, and practice problems with solutions.

### EXCELLING MODULE (Advanced):
Write an advanced deep-dive into "${topic}". Cover higher-order concepts, edge cases, cross-disciplinary connections, and complex problem scenarios. Include at least 2 detailed worked examples with step-by-step solutions. Push towards independent analysis and synthesis.

### DEVELOPING MODULE (Standard):
Write a clear, thorough explanation of core "${topic}" concepts. Use real-world analogies to build understanding. Include 2-3 guided worked examples that progress from basic to moderate difficulty. Bridge theory and application with concrete steps.

### STRUGGLING MODULE (Foundation):
Write a simplified, step-by-step breakdown of the most fundamental "${topic}" concepts. Use everyday analogies. Include 2-3 micro-step examples where each step is explained in plain language. Build from absolute basics — assume minimal prior knowledge.

FORMATTING:
- Use # for module title, ## for major sections, ### for subsections
- Use numbered lists for steps, bullet points for key ideas
- Use **bold** for key terms, > blockquotes for important definitions
- Use --- between major sections
- Each module title should include one relevant emoji

Return ONLY the raw JSON object. No markdown code blocks around it.`;

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "deepseek/deepseek-chat-v3-0324",
        messages: [
          { role: "system", content: "You are an expert curriculum content writer. Generate precise, actionable teaching content in valid JSON format. Write real educational content — no filler, no meta-commentary, no generic tips. Only substantive teaching material." },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 8000,
      }),
    });

    if (!response.ok) {
      const errBody = await response.text();
      throw new Error(`API error ${response.status}: ${errBody}`);
    }

    const result = await response.json();
    let text = result.choices?.[0]?.message?.content || "";
    
    // Extract JSON block aggressively
    const startIndex = text.indexOf('{');
    const endIndex = text.lastIndexOf('}');
    if (startIndex !== -1 && endIndex !== -1) {
      text = text.slice(startIndex, endIndex + 1);
    }

    let parsedPayload;
    try {
      parsedPayload = JSON.parse(text);
    } catch {
      console.error("Parse error, raw text:", text.substring(0, 200));
      parsedPayload = getFallbackModules(topic);
    }

    // ==========================================
    // PASS 2: MiniMax M2.5 — Refinement
    // ==========================================
    let refinedPayload;
    let usedRefiner = false;

    try {
      const refinePrompt = `You are a strict educational content editor. You will receive 3 teaching modules. Your ONLY job is to:
1. Remove any "Learning Outcomes", "Learning Objectives", "Tips", "Self-Assessment", "Quick Check", "Confidence Booster", "Faculty Note" or similar meta-sections. Keep ONLY the actual teaching content.
2. Ensure all content is written in precise, detailed paragraphs with worked examples.
3. Remove generic motivational filler. Keep it academic and substantive.
4. Fix any factual errors.
5. Maintain markdown formatting.

INPUT:
${JSON.stringify(parsedPayload, null, 2)}

Return ONLY a valid JSON object with the exact same 3 keys ("excelling", "developing", "struggling"). No markdown code blocks.`;

      const refineResponse = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "minimax/minimax-m2.5:free",
          messages: [
            { role: "system", content: "You are a strict educational content editor. Return only valid JSON. Improve quality and remove hallucinations without losing detail." },
            { role: "user", content: refinePrompt }
          ],
          temperature: 0.3,
          max_tokens: 8000,
        }),
      });

      if (refineResponse.ok) {
        const refineResult = await refineResponse.json();
        let refineText = refineResult.choices?.[0]?.message?.content || "";
        
        const rStart = refineText.indexOf('{');
        const rEnd = refineText.lastIndexOf('}');
        if (rStart !== -1 && rEnd !== -1) {
          refineText = refineText.slice(rStart, rEnd + 1);
        }

        try {
          refinedPayload = JSON.parse(refineText);
          usedRefiner = true;
        } catch {
          console.warn("Refiner parse failed, using raw DeepSeek output");
          refinedPayload = parsedPayload;
        }
      } else {
        console.warn("Refiner API error, using raw DeepSeek output");
        refinedPayload = parsedPayload;
      }
    } catch (refineErr) {
      console.warn("Refiner call failed:", refineErr.message);
      refinedPayload = parsedPayload;
    }

    return NextResponse.json({
      status: "success",
      subject: topic,
      pipeline: usedRefiner ? "DeepSeek V3 → MiniMax M2.5 Refined" : "DeepSeek V3 (unrefined)",
      modules: refinedPayload
    });

  } catch (error) {
    console.error("Module generation error:", error);
    return NextResponse.json({
      status: "error",
      message: error.message
    }, { status: 500 });
  }
}

function getFallbackModules(topic) {
  return {
    excelling: `### 🌟 Advanced Application: ${topic}\n\n**Learning Objectives:**\n1. Analyze complex ${topic} scenarios with multi-variable constraints.\n2. Evaluate systemic outcomes and identify edge cases.\n3. Create synthesized theoretical models applying ${topic} to real-world datasets.\n\n**Deep Dive Analysis:**\nThis module pushes the boundaries of the standard curriculum. Rather than simple recall, we will apply advanced cognitive frameworks to evaluate how ${topic} functions under stress testing. You are expected to draw connections across multiple disciplines and challenge existing paradigms. High-level synthesis and peer-led discussions will form the core of this learning phase.\n\n**Critical Thinking Challenge:**\nDesign a comprehensive 3-part study exploring the boundary conditions of ${topic}. You must document your methodology, predict potential failure points, and propose alternative architectural solutions.\n\n**Faculty Note:**\nThis student requires intellectual stimulation. Avoid repetitive tasks and focus on independent research opportunities.`,
    developing: `### 📈 Growth Fundamentals: ${topic}\n\n**Learning Objectives:**\n1. Apply ${topic} principles to standard, predictable scenarios.\n2. Analyze core components and understand their functional relationships.\n3. Bridge the gap between theoretical knowledge and practical execution.\n\n**Core Concept Exploration:**\nWe will solidify your understanding of ${topic} by focusing on practical, visual examples. Building strong connective tissue for memory retention requires consistent application. We will break down the abstract concepts into tangible, step-by-step processes that you can easily replicate and adapt.\n\n**Guided Practice & Application:**\nReview the detailed structural diagram provided in class. Next, complete the scenario-based assessment where you will apply ${topic} to solve three distinct, progressively difficult problems. Utilize the hint system if you encounter blockers.\n\n**Faculty Note:**\nProvide structured guidance. The student understands the theory but needs confidence in application. Visual aids and step-by-step breakdowns are highly effective here.`,
    struggling: `### 🎯 Foundation Builder: ${topic}\n\n**Learning Objectives:**\n1. Clearly define and identify the basic foundational elements of ${topic}.\n2. Describe how ${topic} functions using everyday analogies.\n3. Successfully complete guided, single-step exercises.\n\n**Building Blocks & Simplification:**\nLet's break this down into simple, bite-sized pieces. It is completely normal to find ${topic} challenging at first. We will look at it through the lens of a simple everyday analogy. By focusing on one micro-step at a time, we eliminate overwhelming complexity and build true understanding from the ground up.\n\n**Step-by-Step Guided Walkthrough:**\n1. First, we identify the core definition without any jargon.\n2. Second, we look at a real-world example (e.g., how this concept applies to organizing a library or building a bridge).\n3. Third, we solve a basic problem together, explaining the 'why' behind every single action.\n\n**Confidence Check:**\nComplete the 5-minute interactive matching game to lock in these foundational definitions before moving forward. You've got this! We will review your answers together in our next 1-on-1 session.\n\n**Faculty Note:**\nRequires immediate foundational intervention. Use high-praise, low-stakes environments. Avoid complex jargon and rely heavily on analogies.`
  };
}
