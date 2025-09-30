from typing import List

ANS_NORMALIZATION_CACHE = "../data/answer_normalization/all_date_num_caches_gpt4_results_25-01-17.json"
ANS_ALIAS_CACHE = "../data/answer_normalization/alias_answers_cache.json"
ALIAS_ANNOTATION_LOG = "../data/answer_normalization/alias_annotation_log.csv"
COMPARISON_QUESTIONS_VAL_CACHE: str = "../data/answer_norm_comparison_steps/comparison_questions_cache.json"
EXECUTION_LOG_FILE = "../data/discrete_steps/execution_log/execution_log.txt"
LLAMA3_70B_INSTRUCT = "meta-llama/Llama-3-70b-chat-hf"
LLAMA31_405B_INSTRUCT = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
GPT4_TURBO = "gpt-4-1106-preview"
GPT4_OMNI = "gpt-4o"
GPT_41 = "gpt-4.1"
GPT_5 = "gpt-5"
QWEN2_72B_INSTRUCT = "Qwen/Qwen2-72B-Instruct"
QWEN25_72B_INSTRUCT = "Qwen/Qwen2.5-72B-Instruct-Turbo"
GEMMA3_27B = "google/gemma-3-27b-it"
DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1"
DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3"
O1 = "o1"
O3 = "o3"
O1_MINI = "o1-mini"
O3_MINI = "o3-mini"
O4_MINI = "o4-mini"
GEMINI_25_PRO = "gemini-2.5-pro"
GEMINI_25_FLASH = "gemini-2.5-flash"
CLAUDE4_OPUS = "claude-opus-4-20250514"
CLAUDE4_SONNET = "claude-sonnet-4-20250514"
REASONING_LLMS = [O1, O3, O1_MINI, O3_MINI, O4_MINI, DEEPSEEK_R1, GEMINI_25_PRO, GEMINI_25_FLASH, CLAUDE4_OPUS,
                  CLAUDE4_SONNET]
MAX_LEN_RETRIEVAL_PROMPT = 1020000
MAX_TOKENS_GPT4_O = 128000

WORKER_ANSWER_OVERLAP_THRESHOLD = 0.77
WORKER_NUM_ANSWERS_DELTA_THRESHOLD = 0.25
EMPTY_ANSWER = "{}"
LIST_QUESTION = "[list]"
BOOLEAN_TRUE_KEYWORDS = ['yes', 'True', 'true']
BOOLEAN_FALSE_KEYWORDS = ['no', 'False', 'false']
NOANSWER = None
COMPARISON_OPS = ['at least', 'at most', 'higher than', 'lower than', 'more than', 'greater than', 'less than',
                  'equal to', 'in', 'contains']
SUPERLATIVE_OPS = ['highest', 'lowest', 'earliest', 'higher', 'lower']  # included higher/lower for the comparison op
COMPARISON_STEP_OPS = SUPERLATIVE_OPS + ['true', 'false']
ARITHMETIC_OPS = ['sum', 'difference', 'division', 'quotient', 'multiplication', 'product', 'percentage', 'absolute value']
AGGREGATE_OPS = ['sum', 'average', 'mean', 'median', 'highest', 'lowest', 'number', 'different', 'most common']
GROUP_OPS = ['sum', 'average', 'mean', 'median', 'highest', 'lowest', 'number']

ARITHMETIC_OPS_PYTHON = ['addition', 'difference', 'division', 'quotient', 'multiplication', 'product', 'percentage']
GROUP_OPS_PYTHON = ['sum_', 'average', 'mean', 'median', 'max_', 'min_', 'count']

NORM_ANSWER_NUM = "num"
NORM_ANSWER_NUM_RANGE = "num_range"
NORM_ANSWER_DATE = "date"
NORM_ANSWER_DATE_RANGE = "date_range"
NORM_ANSWER_STRING = "string"

MEASUREMENT_UNITS = ["%", "acres", "meter", "meters", "metre", "$", "£", "€", "ft", "feet", "kcal", "kj", "kg", "lbs", "km2", "sq mi", "km", "mi"]
UNKNOWN_ANSWERS = ["unknown", "none"]

FILTER_QS_STR_2024_05_17 = """Name all the battles between the Dutch and English in the First, Second and Third Anglo-Dutch Wars, and list the victor of each battle.
What percentage of European countries were once conquered by Turkish tribes throughout their history?
which four Canadian Prime Ministers have had the highest approval rating in the last 50 years?
How many times since the 1980s was a former NBA #1 draft pick released or traded by the team that selected him after  his first year of playing with the team?
What herbs are commonly used in Vietnamese, Thai and Sichuan cuisine?
What percentage of Emmy Award winning shows for Outstanding drama from 2010-2022 were won by shows about royal families?
How many Asian American actors (and actresses) have won an Oscar in either a supporting or a leading role?
How many women outside of Europe have won the Nobel prize for literature?
Who is the main female protagonist in each of George Eliot's novels?
Do all European cities with more than 1.5 million residents have either a metro or tram?
What was the largest number of Dutch ships used in battle during the Dutch-Portuguese War?
Were more of the last twenty US Presidents born in New England states or Midwestern states?
Have any UK Foreign Secretaries went on to become prime ministers?
Who are the seven Archons in Gnostic belief and what is the origin of each of their names?
How has the annual average percentage of American Nobel prize winners changed over the past century?
How has the percentage of women Nobel prize winners changed over the past 30 years?
Tell me the average expenditure on healthcare, education and housing during the Gordon Brown government compared to those of David Cameron's
What popular Turkish surnames are named after animals?
Which Lord of Light characters are based on Hindu deities?
What were the former occupations of the Booker Prize winners over the past decade?
What's the percentage of Canadian prime ministers that had never served as cabinet ministers before entering office?
How many Joseph Conrad finished novels are set in Southeast Asia?
What percentage of Muslim-majority countries do not have a Sunni majority?
How many of the world's twenty largest yachts are owned by Arab royals?
What celeberities that had a cameo appearance on the TV show Dave were not singers?
Who have been the four longest serving prime ministers of Italy?
Which group in the US is more supportive of gay marriage: Postgrads, Rhode Islanders or people aged eighteen to twenty-nine?
Do people in Midwestern US states support same sex marriage more than those in the deep south?
What is the percentage of seats held by Left-wing parties in each parliament of an EU country?
Which songs have Drake and Rihanna collaborated on?
Which US presidents and vice-presidents were planters or were born to planter families?
What percentage of Swedish queen consorts came from Slavic-language speaking countries?
From 1990-2020, how many times has the US Senate majority flipped to the other party?
Which Ottoman sultans were not the son of the previous sultan?
who was the first non-European and non-American woman to win the Nobel Prize for medicine?
which English monarch had to wait the longest before ascending to the throne in the 17th century?
Which of Mexico's wars began in what can be labeled as a civil war or rebellion?
List the percentage of centers out of the NBA scoring leaders for each decade.
Which two kingdoms were the last to declare war on Sweden during the Great Northern War?
What were the origins of the foreign pharaonic dynasties that ruled over Egypt?
Are any of the novels by Mikhail Bulgakov not satires of the Soviet communist state?
who gained the most territory as a consequence of the Second Balkan War?
What percentage of member states of the Commonwealth do not have English as an official language?
List female poets of Andalusian Spain along with their year of birth and year of death.
Who was the first Asian novelist ever to win a Hugo Award for Best Novel?
Which Ivy League alumni are Nobel prize laureates?
In early 2025, which South American state's parliament has the greatest percentage of seats held by populist parties (either from the left or right)?
What is number of Nobel prize winner alumni of each Ivy league school?
Which of the Shia dynasties of North Africa and the Levant were established by Arab rulers?
List the number of Marvel Comics female superhero debuts by decade.
List all the Roman Imperial dynasties along with the number of years that each dynasty ruled
Which year since 1960 saw the greatest increase in voter turnout for a US Presidential election over the previous election and who was its winner?
How many Greek gods were believed to be the offspring of other gods (not titans)?
What were the heads of the Babylonian, Greek, Norse, Mayan, Japanese and Egyptian pantheons the gods of?
Which Academy award winning directors are women, born outside the US?
What was the average percentage of women Nobel prize laureates in Literature in each decade since 1950?
Which nations in South America have ever been led by an Indigenous American head of state?
What percentage of US presidents elected after 1899 were born in the southern states ?
Who were the great female poets of ancient Greece?
Tales of zombies, banshees, werewolves and vampires originally come from which countries?
Since 2015, what has been the percentage of top 5 NBA drafted players to average more than 15 points in their rookie season?
Who was the first Caliph of each Caliphate and what was their position before ascending the throne?
Listed by date of Theatrical release, chronologically, what are Neil Simon's plays which have also been made into movies
Which Fast and Furious big bads went on to star in multiple films in the series?
What was the combined cost of producing all of The Dark Knight movies?
Which characters on HBO's The Witcher are sorcerers?
Who has killed each of the seven homunculi in Fullmetal Alchemist Brotherhood?
how many descendants of Catherine the Great ruled Russia before the First Russian Revolution?
What has been the average number of children per Spanish monarch during the 1800s compared to the 2000s?
Who were the three longest reigning kings of France?
Was there ever a Swedish King or Queen Regent who have been married more than three times? If so, please list their names
Which British prime minister were known for cheating on their spouses?
Were any of the kings of France ever involved in a war against England (or the UK) as well as in a separate war against Spain during their reign? If so, please tell me which ones."""

