# A3: Concepts

ExpandNet converts source-language lexical/sense annotations into target-language equivalents.
It does this in three steps: translating sentences, aligning source/target tokens, and projecting annotations across the alignment.
You can run each step independently, customize aligners and dictionaries, and manually supply translations if your language pair isn’t supported, thus skipping step 1.

## Step 1 Translate

Takes six arguments:
1. src_data: An XML file containing the sentences to be translated
2. lang_src: The language key for the source language.
3. lang_tgt: The language key for the target language.
4. output_file: The address of the file where the result of the translation will be saved.
5. join_char: The character to use to connect multi-word expressions. Should not be a space.
6. no_pos: The system adds part-of-speech tags by default. Set this flag to skip that step.

Altogether, it can be run as such:

```bash 
python3 expandnet_step1_translate.py \
--src_data res/data/xlwsd_se13.xml \
--lang_src en \
--lang_tgt es \
--output_file expandnet_step1_translate.out.tsv \
--join_char _ \
--no_pos
```

## Translation Output

The output of the translation step is a tsv file with columns named: 'sentence_id', 'text', 'translation', 'lemma', 'translation_token', 'translation_lemma' and, optionally, 'translation_pos'. These columns should be tab-separated. The sentence id should be a unique identifier. 

- **sentence_id**: unique identifier of the source sentence.
- **text**: raw source-side text.
- **translation**: raw translation.
- **lemma**: space-separated source-language lemmas.
- **translation_token**: space-separated target-language tokens.  
  - If a token contains spaces, replace them using the `join_char` (e.g., underscores).  
  - This same character must be used consistently in later steps.
- **translation_lemma**: space-separated target-side lemmas.
- **translation_pos** (optional): space-separated target-side POS tags, using either  
  - the Universal POS tagset (17 tags), or  
  - the simplified tagset: `n`, `a`, `j`, `r`, `x`.


**If Step 1 is unsupported for your language pair, you may create a file of this format on your own, and continue to Step 2.**

Here is an example:


```tsv
sentence_id	text	translation	lemma	translation_token	translation_lemma	translation_pos
d000.s001	I ran	Yo corrí	I run	Yo corrí	yo correr	PRON VERB
```

## Step 2 Align

For the alignment step, it is recommended to use DBAlign, for which a dictionary is required.
Dictionaries must be .tsv files, where each row contains a source-side word, then a tab character, then a space-separated list of possible target-side words that it may be translated as. Underscores should be used in place of spaces for multi-word expressions, or any tokens with spaces within them.
An example dictionary, `wikpan-en-es.tsv` is included to demonstrate the format these dictionaries should take.

### Note
Please refer to `requirements.txt` for dependencies. For this step, you may need to download additional spaCy language models.
You can do this with:

```bash
python3 -m spacy download <MODELNAME>
```

The models employed in the code by default are: en_core_web_lg, es_core_news_lg, fr_core_news_lg, it_core_news_lg, ro_core_news_lg, zh_core_web_lg, xx_ent_wiki_sm.

Takes seven arguments:
1. translation_df_file: The address of the .tsv created by Step 1 (or created independently if working with an unsupported language pair)
2. lang_src: The language key for the source language (default 'en').
3. lang_tgt: The language key for the target language (default 'fr').
4. aligner: The aligner to be used, one of 'simalign' or 'dbalign'.
5. dict: If using dbalign, the multilingual dictionary which it will use, or 'bn' to use BabelNet as this dictionary (if available). 
6. output_file: The address of the file where the result of the alignment step will be saved.
7. join_char:  The character to use to connect multi-word expressions. Should not be a space.

Altogether, it can be run as such:

```bash 
python3 expandnet_step2_align.py \
--translation_df_file expandnet_step1_translate.out.tsv \
--lang_src en \
--lang_tgt es \
--aligner dbalign \
--dict res/dicts/wikpan-en-es.tsv \
--output_file expandnet_step2_align.out.tsv \
--join_char _
```

## Step 3: Projection

The projection step takes the output of **Step 2 (alignment)** and uses it to transfer sense annotations or lexical information from the source language to the target language.

This script has **seven required arguments** plus four **optional flags** that toggle different filtering behaviors.

---

### **Required Arguments**

1. **src_data**  
   The original XML file containing the source-language sentences (the same file used in Step 1).

2. **src_gold**  
   The gold key file containing the source-language sense annotations.

3. **dictionary**  
   The bilingual dictionary used for lexical projection (typically the same `.tsv` dictionary used in Step 2).

4. **alignment_file**  
   The alignment output file produced in Step 2.

5. **output_file**  
   Path to the file where projected annotations will be saved.

6. **join_char**  
   Character used to join multi-word lexical items during projection (default: `_`).

7. **token_info_file**  
   Path to the file where detailed token-level logs will be written.

---

### **Optional Flags**

These flags toggle different filtering screens.  
By default, **all filters are ON**.  
Passing a flag turns **OFF** the corresponding filter.

- **`--no_pos_screen`**  
  Turn off part-of-speech filtering. Normally, projections are rejected when the source and target POS differ. Requires POS information from previous steps.

- **`--no_ne_screen`**  
  Turn off named-entity filtering (which normally filters out capitalized named entities).

- **`--no_dict_screen`**  
  Turn off dictionary-based filtering. Normally, only dictionary-supported translations are projected.

- **`--no_oov_screen`**  
  Allow projection of English lexical items not found in the dictionary (OOV items).  
  By default, OOV English terms are not projected.



```bash 
python3 expandnet_step3_project.py \
--src_data res/data/xlwsd_se13.xml \
--src_gold res/data/se13.key.txt \
--dictionary res/dicts/wikpan-en-es.tsv \
--alignment_file expandnet_step2_align.out.tsv \
--output_file expandnet_step3_project.out.tsv \
--join_char _ \
--token_info_file expandnet_step3_project.token_info.out.tsv
```

## eval_release.py

Takes two arguments:
1. A gold-standard file, listing the acceptable target-language senses for each synset. Format: [synset ID] [TAB] [lemmas, space separated]
2. An output file, listing exactly one sense per line. Format: [synset ID] [TAB] [lemma]

Output is an evaluation for each sense, and overall statistics.

```bash 
python eval_release.py res/data/se_gold_es.tsv expandnet_step3_project.out.tsv
```
