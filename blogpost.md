## **MoNaCo: More Natural Questions for Reasoning Across Dozens of Documents**

- *Check out [our blogpost](https://medium.com/ai2-blog/break-mapping-natural-language-questions-to-their-meaning-representation-31bb753701d6) at the official [Ai2 blog!](https://medium.com/ai2-blog)*  

We introduce **MoNaCo**, a benchmark of **Mo**re **Na**tural and **Co**mplex questions to evaluate the question-answering (QA) skills of language models. MoNaCo contains 1,315 time-consuming questions whose solutions involve combining and reasoning over information spanning across dozens of Wikipedia tables and passages.

Large language models (LLMs) are emerging as the go-to tool for answering questions and surfacing hard-to-find information. While LLMs (and LLM-powered applications such as [Deep Research](https://gemini.google/overview/deep-research/)) hold great promise in solving problems that require combining knowledge from hundreds of sources, such problems are poorly represented in most model evaluation benchmarks. Existing QA benchmarks rarely feature realistic questions that are both fact-reliant and genuinely time-intensive for humans to answer. Instead, most benchmark questions are too simplistic, requiring only a handful of evidence documents, while the more complex QA benchmarks are typically machine-generated—which may result in contrived and unnatural questions.


MoNaCo addresses this gap, presenting realistic questions whose solution spans up to hundreds of documents. Furthermore, it reveals key limitations in the question-answering abilities of frontier LLMs.


<center>
    <a href="https://tomerwolgithub.github.io/monaco/images/blog/blogpost_01.png"> 
        <img src="images/blog/blogpost_01.png" height="300">
     </a>
</center>


In our experiments, we tested 15 frontier LLMs on MoNaCo, including GPT-5, o3, Claude Opus 4, Gemini 2.5 Pro, and Deepseek-R1. All models struggled, with the top-performing LLM, o3, reaching an F1 score of 61.2% while answering only 38.7% of examples with a perfect score.

We also observe that as solutions to questions entail reasoning over more intermediate answers or require more evidence sources, model performance decreases substantially.

<center>
    <a href="https://tomerwolgithub.github.io/monaco/images/blog/blogpost_02.png"> 
        <img src="images/blog/blogpost_02.png" height="200">
     </a>
</center>


### **About the MoNaCo Benchmark**

We created MoNaCo as a QA benchmark with questions that are:  

1. **Realistic**, reflecting the information-seeking goals of real-world users
2. **Time-consuming**, with questions that cannot be answered without potentially hundreds of intermediate facts

For example, while the two MoNaCo questions below have succinct answers, they both require dozens of fact-finding steps:

<center>
    <a href="https://tomerwolgithub.github.io/monaco/images/blog/blogpost_03.png"> 
        <img src="images/blog/blogpost_03.png" height="300">
     </a>
</center>

Overall, MoNaCo has 1,315 questions whose solutions involve many intermediate steps that span across dozens, and at times hundreds, of evidence documents. Compared to traditional QA benchmarks, the scope of MoNaCo questions is much broader. To solve them, models must be proficient at decomposing complex queries, locating hundreds of pieces of information, and reasoning, combining, and aggregating this data effectively.

MoNaCo’s breadth and depth makes it ideal as an LLM benchmark for at least five different settings:

* Evaluating models’ **parametric knowledge** and reasoning
* Measuring complex **reasoning over long contexts**, where all of the evidence docs are provided in the context
* **Multi-document retrieval** performance
* End-to-end **retrieval-augmented generation** (RAG)
* **Training Deep Research-like systems**, using the gold standard reasoning chains


### **Human-Annotated Reasoning Chains**

Unlike other QA benchmarks, all questions in MoNaCo come with gold-standard, human-annotated reasoning chains. Namely, for each question, we provide all the intermediate steps for its solution, as well as the answers and supporting evidence documents. 

Reasoning chains are expressed as a series of [decomposition steps](https://aclanthology.org/2020.tacl-1.13/). In the figure below, we see part of the decomposition of an example question: “In European countries, are current left-wing political parties more likely to be headed by women than right-wing ones?” Each step is either an intermediate question (**qa_model**) or a Python function representing a query operation (**filter**, **count**). For question steps, we provide human-annotated answers and supporting sentences/tables from Wikipedia, while for query operation steps, we provide their full execution results. 

<center>
    <a href="https://tomerwolgithub.github.io/monaco/images/blog/blogpost_04.png"> 
        <img src="images/blog/blogpost_04.png" height="300">
     </a>
</center>

Note that the reasoning chain of the example question would be extremely time-consuming for any person to follow. Answering this question entails reviewing all political parties in each European country to note their affiliation and the leader's gender, drawing on the equivalent of 719 Wiki pages.

<center>
    <a href="https://tomerwolgithub.github.io/monaco/images/blog/blogpost_05.png"> 
        <img src="images/blog/blogpost_05.png" height="300">
     </a>
</center>


### **Data Collection and Composition**

Collecting realistic and many-step questions “in the wild” for a benchmark like MoNaCo is hard. Users tend to shy away from entering such queries into search engines, and recording them from user-AI interactions—most of which are private—poses added challenges. 


For MoNaCo, we relied on annotators to write questions that reflect real-world users’ information-seeking goals. Specifically, we asked Amazon Mechanical Turk workers to write questions that would interest a particular target persona. By priming workers to assume a specific persona and not use pre-defined templates, we encouraged these workers to come up with realistic questions—helping diversify our data.



