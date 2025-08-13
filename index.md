## **Reasoning across Dozens of Documents**

MoNaCo, a benchmark of More Natural and Complex questions to evaluate the question-answering (QA) skills of language models. MoNaCo contains [1,315](https://huggingface.co/datasets/allenai/MoNaCo_Benchmark) time-consuming questions whose solutions involve combining and reasoning over information spanning across dozens of Wikipedia tables and passages. Compared to traditional QA benchmarks, the scope of MoNaCo questions is much broader. To solve them, models must be proficient at decomposing complex queries, locating hundreds of pieces of information, and reasoning, combining, and aggregating this data effectively.
This benchmark was created by a team of [NLP researchers](#authors) at the [University of Pennsylvania](https://cogcomp.seas.upenn.edu/), the [Allen Institute for AI](https://allenai.org/), [Tel Aviv Univeristy](https://mega002.github.io/) and [Bar-Ilan University](https://nlp.biu.ac.il/~rtsarfaty/onlp).


For more details on Break, please refer to our [TACL 2025 paper](#paper), and to our [Ai2 blogpost](#paper).  

<center>
    <a href="https://allenai.github.io/Break/images/qdmr01.png"> 
        <img src="images/monaco_logo.jpeg" height="170">
      </a>
</center>

## **Question-Answering Datasets**

The Break dataset contains questions from the following 10 datasets:  
* **Semantic Parsing**: [Academic](https://github.com/jkkummerfeld/text2sql-data), [ATIS](https://github.com/jkkummerfeld/text2sql-data), [GeoQuery](https://github.com/jkkummerfeld/text2sql-data), [Spider](https://yale-lily.github.io/spider)
* **Visual Question Answering**: [CLEVR-humans](https://cs.stanford.edu/people/jcjohns/clevr/), [NLVR2](http://lil.nlp.cornell.edu/nlvr/)
* **Reading Comprehension (and KB-QA)**: [ComQA](http://qa.mpi-inf.mpg.de/comqa/), [ComplexWebQuestions](https://www.tau-nlp.org/compwebq), [DROP](https://allennlp.org/drop), [HotpotQA](https://hotpotqa.github.io/)  

For the full dataset statistics please refer to our [repository](https://github.com/allenai/Break).


## **Paper**

[**MoNaCo: More Natural and Complex Questions for Reasoning Across Dozens of Documents**](https://arxiv.org/abs/2001.11770v1)  
Tomer Wolfson, Harsh, Trivedi, Mor Geva, Yoav Goldberg, Dan Roth, Tushar Khot, Ashish Ashish Sabharwal and Reut Tsarfaty  
*To appear in the Transactions of the Association for Computational Linguistics (TACL), 2025*  

```markdown
@article{wolfson-etal-2025-monaco,
    title = "MoNaCo: More Natural and Complex Questions for Reasoning Across Dozens of Documents",
    author = "Wolfson, Tomer  and
      Trivedi, Harsh  and
      Geva, Mor  and
      Goldberg, Yoav  and
      Roth, Dan  and
      Khot, Tushar  and
      Sabharwal, Ashish  and
      Tsarfaty, Reut",
    journal = "Transactions of the Association for Computational Linguistics",
    address = "Cambridge, MA",
    publisher = "MIT Press",
    year="2025",
}
```

## **Authors**

<div>
<div class="card">
  <img src="images/authors/author_01.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://tomerwolgithub.github.io/">
    <h4><b>Tomer Wolfson</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_02.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://harshtrivedi.me/">
    <h4><b>Harsh <br>Trivedi</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_03.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://mega002.github.io/">
    <h4><b>Mor <br>Geva</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_04.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://www.cs.bgu.ac.il/~yoavg/uni/">
    <h4><b>Yoav Goldberg</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_05.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://www.cis.upenn.edu/~danroth/">
    <h4><b>Dan <br>Roth</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_06.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://tusharkhot.github.io/">
    <h4><b>Tushar Khot</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_07.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://www.cs.cornell.edu/~sabhar/">
    <h4><b>Ashish Sabharwal</b></h4>  
    </a>
  </div>
</div>
<div class="card">
  <img src="images/authors/author_08.jpg" alt="Avatar" style="width:100%">
  <div class="container">
    <a href="https://nlp.biu.ac.il/~rtsarfaty/onlp">
    <h4><b>Reut Tsarfaty</b></h4>  
    </a>
  </div>
</div>
</div>


## **Leaderboard**

### **Submission**
Evaluating predictions for the hidden test set is done via the [AI2 Leaderboard page](https://leaderboard.allenai.org/).
Log on to the leaderboard website and follow the submission instructions.
* **[Break Leaderboard](https://leaderboard.allenai.org/break/)**
* **[Break High-Level Leaderboard](https://leaderboard.allenai.org/break_high_level/)**  

*Given the GED metric is computed by an approximation algorithm, the evaluation may take several hours. The approximation algorithm also results in slightly different GED values than the paper.*

### **Results**

**Break**

Rank | Submission | Created | EM Dev. | EM Test | SARI Dev. | SARI Test | GED Dev. | GED Test 
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
1 | Curriculum-trained CopyNet <br>*Chris Coleman and Alex Reneau,*<br>*Northwestern University* | Jul 1, 2020 | **`_`**  | **`0.163`** | **`_`**  | **`0.757`** | **`_`**  | **`0.271`** 
2 | CopyNet <br>*([Wolfson et al., TACL 2020](https://arxiv.org/abs/2001.11770v1))* | Feb 1, 2020 | **`0.154`**  | `0.157` | **`0.748`**  | `0.746` | **`0.318`**  | `0.322` 
3 | RuleBased <br>*([Wolfson et al., TACL 2020](https://arxiv.org/abs/2001.11770v1))* | Feb 1, 2020 | `0.002`  | `0.003` | `0.508`  | `0.506` | `0.799`  | `0.802`  


**Break High-level**

Rank | Submission | Created | EM Dev. | EM Test | SARI Dev. | SARI Test | GED Dev. | GED Test 
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
1 | CopyNet <br>*([Wolfson et al., TACL 2020](https://arxiv.org/abs/2001.11770v1))* | Feb 1, 2020 | **`0.081`**  | **`0.083`** | **`0.722`**  | **`0.722`** | **`0.319`**  | **`0.316`** 
2 | RuleBased <br>*([Wolfson et al., TACL 2020](hhttps://arxiv.org/abs/2001.11770v1))* | Feb 1, 2020 | `0.010`  | `0.012` | `0.554`  | `0.554` | `0.659`  | `0.652`  

## **Explore**

To view (many) more question decomposition examples, [explore Break](/explore.md).

## **Download**

- For the full documentation of the dataset and its format please refer to our [HuggingFace repository](https://huggingface.co/MoNaCo-Release/).
