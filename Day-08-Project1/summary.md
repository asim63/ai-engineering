# Day 08- Review and Project
- Reviewed the first week and read all the markdown files of each day.
- Revised concepts and strengthen the fundamental concept on LLM and prompting

## Email Subject Line Generator
From the observations:
- Basic prompting generated a suitable subject line with the lowest prompt complexity and relatively low token usage.
- Role prompting slightly improved the professionalism and marketing style of the generated subject line without significantly increasing token usage.
- Few-shot prompting produced one of the most concise and relevant subject lines, but required substantially more prompt tokens because of the included examples.
- XML formatting improved prompt structure and readability but did not provide a significant improvement in output quality for this task.
- JSON prompting generated a structured response that can be directly parsed by applications, while also achieving the fastest response time among all tested prompts.

### Conclusion
For this task, JSON prompting provided the best balance between output quality, response structure, token cost, and response time.
Few-shot prompting generated high-quality results but was considerably more expensive in terms of token usage. Therefore, it may be preferable only when additional reliability is required.
Basic and role prompting were sufficient for simple subject-line generation tasks, while XML formatting mainly improved prompt organization rather than model performance.