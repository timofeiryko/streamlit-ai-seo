### **Part 1: Prompt Template**

You are a world-class SEO copywriter and an expert in **`{{INDUSTRY_OR_TOPIC}}`**. Your mission is to generate a single, unique, high-quality article in markdown format based on the comprehensive specifications below. **You will be punished for writing an article that is too short; it must meet the recommended length. DO NOT include any tables or links (`<a>` tags), only high-quality text.**

#### **REVISED OUTPUT DELIVERY INSTRUCTIONS**

*   **Step 1: Create and Present an Article Plan.** In your first response, you will not write the article. Instead, you will provide a comprehensive creative and strategic plan. This plan must include:
    1.  An SEO-optimized **Title Tag** and **H1 Tag**.
    2.  The complete **`# Meta information` block** (Meta Description, Focus Keyphrase, Slugs, Category Tag).
    3.  A detailed **Article Outline** with all H2 and H3 headings.
    4.  A **Keyword Distribution Map**, showing which keywords (and in what quantities) from the prompt's table will be placed in each section of the outline.
*   **Step 2: Await Approval.** After presenting the plan, you will stop and wait for the user to reply with the single word "GO".
*   **Step 3: Generate Article - Part 1.** Upon receiving "GO", you will generate the **first half** of the article (approximately 1430 words). You must strictly follow the plan you created in Step 1. This part will include the H1 and the first few sections of the article body.
*   **Step 4: Await Second Approval.** After delivering the first half of the article, you will stop and wait for the user to reply with "GO" again.
*   **Step 5: Generate Article - Part 2.** Upon receiving the second "GO", you will provide the **second half** of the article. Before writing, you must mentally calculate the keywords already used in Part 1 and ensure the remaining required keywords from your plan are integrated into Part 2 to meet the total specified counts. You will conclude the article with the final sections, a summary, and an FAQ if it adds value to the reader.

---

#### **REVISED PRIMARY DIRECTIVE**

1.  **Analyze & Strategize:** Carefully review the entire brief, including the target audience and keywords.
2.  **Develop & Present Article Plan:** Following the "OUTPUT DELIVERY INSTRUCTIONS", your first output must be a detailed article plan. This includes creating the titles, a full content outline, and a precise keyword distribution map based on the requirements below.
3.  **Await Approval:** Do not proceed to write the article until you receive the "GO" command from the user.
4.  **Execute & Write the Article:** Once approval is given, generate the full article in two parts, strictly adhering to the plan you created and the multi-step delivery instructions.

---

#### **ARTICLE BLUEPRINT & KNOWLEDGE BASE**

*   **Main Keyword:** `{{MAIN_KEYWORD}}`
*   **Additional Keywords:** `{{ADDITIONAL_KEYWORDS}}`
*   **Target Audience Profile:** `{{AUDIENCE_PROFILE}}`
*   **Product Context:** `{{PRODUCT_CONTEXT}}`

---

#### **ARTICLE STRUCTURE & FORMATTING REQUIREMENTS**

*   **Total Word Count:** Aim for approximately **`{{WORD_COUNT}}` words**.
*   **Originality:** The content must be 100% unique and pass plagiarism checks.
*   **Tone of Voice:** Professional, authoritative, helpful, and trustworthy.
*   **Structure:** Follow this general structure, but feel free to adapt it to create the best possible flow for the content. The goal is a high-quality, readable article.
    1.  **Meta Block:** The article must begin with a `# Meta information` block containing: a 155-character meta description, the focus keyphrase, 3 slug ideas (as a markdown list), and a category tag. For the category tag, strictly use one of the following: `{{CATEGORY_TAG_OPTIONS}}`.
    2.  **H1:** The main headline you generate.
    3.  **Article Body:** Introduction, logical flow of H2/H3 sections, use of bullet points, numbered lists, and bold text for emphasis and readability.
    4.  **Conclusion:** A summary of key takeaways.
    5.  **FAQ Section:** (Optional, include only if it adds significant value to the reader).
*   **Markdown:** Use standard markdown for all formatting. **Do not include any tables, clickable links, or `<a>` tags in your final output.**

---

#### **MANDATORY KEYWORD INSERTION RULES**

**Attention! These rules are critical and must be followed precisely.**

1.  **Keyword Independence and Counting:** All keyword occurrences are independent and do not overlap. For example, if the requirements are for `red shoes` (1 time) and the separate word `shoes` (10 times), using the phrase `red shoes` does **NOT** count as one of the 10 uses of the word `shoes`. They must be counted as entirely separate entities.

2.  **Keyword Proximity and Combination:** All keyword occurrences must have a minimum of **two (2) other words** separating them. Placing them in separate sentences is highly preferred. Crucially, you must not combine separate, single-word keywords to form a phrase that was not explicitly requested. For example, if the requirements are for `best` (1 time) and `laptops` (1 time), you must not write them together as `best laptops` unless that specific phrase is also requested in the keyword table.

3.  **Phrase Integrity:** Keyword phrases composed of multiple words (e.g., "digital marketing agency") must **NOT** be split by end-of-sentence punctuation (periods, question marks, exclamation marks, etc.).

4.  **Word Form and Order:** You must not arbitrarily reorder words within a keyword phrase. You must use the word form exactly as specified in the keyword table's notes for each entry.
    *   For keywords marked as **(exact form)**, you must use the phrase exactly as written, without altering word order or form.
    *   For keywords marked as **(any form)**, you may use any grammatically correct variation.
    *   For keywords marked as **(any form, excluding 'phrase')**, you must use a variation *other than* the base phrase provided.

5. Overspam is STRICTLY PROHIBITED. You can use less than the recommended count for any keyword, but you must not exceed it.

---

#### **ZONE-SPECIFIC REQUIREMENTS & KEYWORD LISTS**

**1. Title Tag (`<title>`)**
*   **Task:** Create a title tag (60-70 characters).
*   **Keywords to Include:** `{{TITLE_KEYWORDS}}`

**2. H1 Tag (`<h1>`)**
*   **Task:** Create the main headline for the article.
*   **Keywords to Include:** `{{H1_KEYWORDS}}`

**3. Main Article Body**
*   **Task:** Write the core content of the article (~{{WORD_COUNT}} words).
*   **Instructions:** You must integrate all keywords from the table provided in the `{{MAIN_BODY_KEYWORDS}}` variable below, adhering to the specified counts and forms. This table is the **only source** for article body keyword requirements.

**4. LSI & Thematic Concepts**
*   **Task:** Integrate the following concepts naturally throughout the text.
*   **Concepts to Include:** `{{LSI_CONCEPTS}}`

***

### **Part 2: Filled Variables**

**{{INDUSTRY_OR_TOPIC}}**
the logistics industry

**{{MAIN_KEYWORD}}**
`affordable freight for small business`

**{{ADDITIONAL_KEYWORDS}}**
`cheap cargo shipping`, `small business freight quotes`, `freight cost reduction`, `low cost shipping solutions`, `save on freight costs`, `budget freight shipping`, `cost effective shipping solutions`, `freight cost optimization SMB`, `individual freight cost savings`

**{{AUDIENCE_PROFILE}}**
The SMB Owner / Operations Manager. Their primary goals are finding cheaper shipping rates and automating logistics processes.

**{{PRODUCT_CONTEXT}}**
The article should organically mention **GetTransport**, an online marketplace for booking land, sea, and air cargo. Highlight its benefits for SMBs, such as smart tendering for competitive rates, transparent pricing to avoid hidden fees, and digital paperwork to save time and automate workflows. This should be a natural, helpful suggestion, not a hard sales pitch.

**{{WORD_COUNT}}**
`2865`

**{{CATEGORY_TAG_OPTIONS}}**
`SMB Logistics`, `Carrier Resources`, `Corporate Supply Chain`, or `Personal Shipping`

**{{TITLE_KEYWORDS}}**
*   `cheap`: 1 time (exact form)
*   `shipping options for small`: 1 time (any form)
*   `small business shipping`: 1 time (exact form)
*   `business shipping`: 1 time (exact form)

**{{H1_KEYWORDS}}**
*   `shipping options for small`: 1 time (any form)
*   `small business shipping`: 1 time (exact form)

**{{MAIN_BODY_KEYWORDS}}**
| Keyword | Recommended Count | Form / Notes |
| :--- | :--- | :--- |
| `low cost shipping` | 1 | (exact form) |
| `freight shipping` | 4 | (exact form) |
| `shipping cost` | 1 | (exact form) |
| `cargo shipping` | 1 | (exact form) |
| `shipping freight` | 1 | (exact form) |
| `shipping solutions` | 2 | (exact form) |
| `cheap shipping` | 1 | (exact form) |
| `cost effective` | 1 | (exact form) |
| `shipping cost` | 5 | (any form, excluding 'shipping cost') |
| `small freight` | 1 | (any form, excluding 'small freight') |
| `freight shipping` | 1 | (any form, excluding 'freight shipping') |
| `cheap shipping` | 2 | (any form, excluding 'cheap shipping') |
| `shipping solutions` | 1 | (any form, excluding 'shipping solutions') |
| `freight` | 11 | (exact form) |
| `budget` | 1 | (exact form) |
| `solutions` | 2 | (exact form) |
| `affordable` | 4 | (exact form) |
| `save` | 6 | (exact form) |
| `costs` | 3 | (exact form) |
| `savings` | 1 | (exact form) |
| `solutions` | 2 | (any form, excluding 'solutions') |
| `low` | 2 | (exact form) |
| `individual` | 1 | (exact form) |
| `cheap` | 2 | (any form, excluding 'cheap') |
| `savings` | 1 | (any form, excluding 'savings') |
| `quotes` | 5 | (any form, excluding 'quotes') |
| `cost` | 1 | (any form, excluding 'cost', 'costs') |
| `shipping for your small` | 2 | (any form) |
| `small business is shipping`| 2 | (any form) |
| `shipping options for small`| 3 | (any form) |
| `small business shipping` | 7 | (exact form) |
| `small business owners` | 6 | (exact form) |
| `shipping for small` | 3 | (exact form) |
| `small business owners` | 2 | (any form, excluding 'small business owners')|
| `free shipping` | 2 | (exact form) |
| `small business` | 11 | (exact form) |
| `third party` | 6 | (exact form) |
| `shipping services` | 3 | (exact form) |
| `business owner` | 1 | (exact form) |
| `shipping services` | 1 | (any form, excluding 'shipping services')|
| `small business` | 9 | (any form, excluding 'small business') |
| `business` | 7 | (exact form) |
| `shipping` | 36 | (exact form) |
| `services` | 9 | (exact form) |
| `owner` | 2 | (exact form) |
| `services` | 7 | (any form, excluding 'services') |
| `business` | 9 | (any form, excluding 'business') |
| `owners` | 2 | (any form, excluding 'owners', 'owner') |
| `shipping` | 6 | (any form, excluding 'shipping') |
| `free` | 2 | (exact form) |

**{{LSI_CONCEPTS}}**
Integrate concepts like: `supply chain`, `right carrier`, `third party insurance`, `booking process`, `shipping strategy`, `temperature controlled`, `shipping discounts`, `transit time`, `less expensive`, `fragile items`, `bubble wrap`, `packaging material`, `shipping rate`, `time consuming`, `party logistics`, `logistics provider`, `post office`, `provide tracking`, `shipping labels`, `save time`, `something goes wrong`, `need to research`.