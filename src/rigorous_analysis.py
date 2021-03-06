# rigorous_analysis.py
# Rigorous Analysis!
# Gil Walzer

import re

import nltk, codecs, json

from spacycaller import SpacyCaller
from parse_vendors import Vendor
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

class Analysis:

    flat_attributes = ["feedback", "months", "rank", "fans", "transactions", "word_count", "sentence_count", "np_count", "verb_count",
                "avg_num_of_clauses", "avg_sentence_length", "avg_word_length", "avg_length_np", "pausality",
                "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref", "e",
                "ppos", "pneg", "pneu", "pcom", "rpos", "rneg", "rneu", "rcom"]

    def __init__(self, fans, transactions, feedback, rank, months, vendor_id, username, quantity, pos_counts, complexity, uncertainty, nonimmediacy, emotiveness, diversity, profile_sentiments, review_sentiments):
        self.quantity = quantity
        self.pos_counts = pos_counts
        self.complexity = complexity
        self.uncertainty = uncertainty
        self.diversity = diversity
        self.nonimmediacy = nonimmediacy
        self.emotiveness = emotiveness
        self.profile_sentiments = profile_sentiments
        self.review_sentiments = review_sentiments

        self.fans = fans
        self.rank = rank
        self.transactions = transactions
        self.feedback = feedback
        self.months = months
        self.vendor_id = vendor_id
        self.username = username

    """ expects list of strings """
    def make_input_vector(self, attrs):
        param_list = []
        params, param_tup = self.flatten()
           
        for each in attrs:
            if each not in params:
                pass
            param_list.append(params[each])

        param_tuple = tuple(n for n in param_list)
        
        return param_tuple

    def flatten(self):
        feedback = 0
        months = 1

        try:
            months = int(self.months)
            feedback = float(self.feedback)

        except ValueError:
            pass

        rank = self.rank
        if rank is '' or rank is u'':
            rank = 100.0
            
        transactions = self.transactions
        fans = self.fans

        pc = self.pos_counts

        q = self.quantity               # 4

        word_count = q[0]
        np_count = q[1]
        sentence_count = q[2]
        verb_count = pc[0]

        c = self.complexity             # 5
        avg_num_of_clauses = c[0]
        avg_sentence_length = c[1]
        avg_word_length = c[2]
        avg_length_np = c[3]
        pausality = c[4]

        u = self.uncertainty            # 3
        uncertainty_count = float(u[0])
        other_ref = u[1]
        modal_count = pc[4]

        d = self.diversity              # 2
        lex_d = d[0]
        con_d = d[1]

        n = self.nonimmediacy           # 2

        if word_count is 0:
            self_ref, group_ref = 0,0
        else:
            self_ref = n[0]*1.0 / word_count
            group_ref = n[1]*1.0 / word_count

        e = self.emotiveness            # 1 

        ps = self.profile_sentiments    # 5
        ppos = ps["pos"]
        pneg = ps["neg"]
        pneu = ps["neu"]
        pcom = ps["compound"]

        rs, rpos, rneg, rneu, rcom = 0,0,0,0,0
        rs_both = self.review_sentiments     # 4
        if rs_both is not None:
            avg_rating = rs_both[0]
            rs = rs_both[1]
            rpos = rs["pos"]
            rneg = rs["neg"]
            rneu = rs["neu"]
            rcom = rs["compound"]
                                                # 23 = total 

        flat_tuple = (feedback, months, rank, fans, transactions, word_count, sentence_count, np_count, verb_count, 
                avg_num_of_clauses, avg_sentence_length, avg_word_length, avg_length_np, pausality,
                uncertainty_count, other_ref, modal_count, lex_d, con_d, self_ref, group_ref, e,
                ppos, pneg, pneu, pcom, rpos, rneg, rneu, rcom)

        flat_dict = {"feedback": feedback, "months": months, "rank": rank, "fans": fans, "transactions": transactions, 
                "word_count": word_count, "sentence_count": sentence_count, "np_count": np_count, "verb_count": verb_count, 
                "avg_num_of_clauses": avg_num_of_clauses, "avg_sentence_length": avg_sentence_length, 
                "avg_word_length": avg_word_length, "avg_length_np": avg_length_np, "pausality": pausality,
                "uncertainty_count": uncertainty_count, "other_ref": other_ref, "modal_count": modal_count,
                "lex_d": lex_d, "con_d": con_d, "self_ref": self_ref, "group_ref": group_ref, "e": e,
                "ppos": ppos, "pneg": pneg, "pneu": pneu, "pcom": pcom, "rpos": rpos, "rneg": rneg, 
                "rneu": rneu, "rcom": rcom}
        return flat_dict, flat_tuple

class Analyzer:
    def __init__(self):
        self.spacy = SpacyCaller()
        
    def analyze(self, vendor):

        tokens = self.spacy.spacy_analyze_vendor(vendor)
    
        pos_count_tuple = pos_counts(tokens)
        quantity = quantity_analysis(tokens)
        complexity = complexity_analysis(tokens, vendor)
        uncertainty = uncertainty_analysis(tokens)
        nonimmediacy = nonimmediacy_analysis(tokens)
        emotiveness = emotiveness_analysis(pos_count_tuple)
        diversity = diversity_analysis(tokens)

        profile_sentiments = profile_sentiment_analysis(vendor)

        review_sentiments = review_sentiment_analysis(vendor)
        
 
        fans = vendor.fans
        transactions = vendor.transactions
        feedback = vendor.feedback
        months = vendor.months
        vendor_id = vendor.id
        username = vendor.username
        rank = vendor.rank

        return Analysis(fans, transactions, feedback, rank, months, vendor_id, username, quantity, pos_count_tuple, complexity, uncertainty, nonimmediacy, emotiveness, diversity, profile_sentiments, review_sentiments)
    
    def __str__(self):
        return self.__dict__

    

def create_Analysis_from_json(jsons):
    a = json.loads(jsons)
    
    analysis = Analysis(a["fans"], a["transactions"], a["feedback"], a["rank"], a["months"], a["vendor_id"],
    a["username"], a["quantity"], a["pos_counts"], a["complexity"], a["uncertainty"],
    a["nonimmediacy"], a["emotiveness"], a["diversity"], a["profile_sentiments"], a["review_sentiments"])
    return analysis

def get_content_words(tokens):
    content_POS_list = ["FW", "JJ", "JJR", "JJS", "NN", "MD", "NNP", "NNPS", "NNS", "RB", "RBR", "RP", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "SYM"]
    
    content_words = []
    for token in tokens:
        pos = token.tag_
        if pos in content_POS_list:
            content_words.append(token)
            
    return content_words
    
# actually takes any iterable
def frequencies(tokens):
    s = {}
    for token in tokens:
        if token.text in s:
            s[token.text] = s[token.text] + 1
        else:
            s[token.text] = 0

    return s

def profile_sentiment_analysis(vendor):
    profile = vendor.profile
    profile = profile.encode(errors="ignore")
    vs = vaderSentiment(profile)

    return vs

def review_sentiment_analysis(vendor):
    review_list = vendor.reviews
    rating_sum = 0.0
    num_ratings = 0.0
    
    if len(review_list) is 0:
        return None
    
    sent_sum = {"pos":0.0, "neg":0.0, "neu":0.0, "compound":0.0}
    for review in review_list:
        message = review[1]
        message = message.encode(errors="ignore")
        rating = review[0]

        vs = vaderSentiment(message)
        
        if not (vs["neu"] is 1.0 and vs["compound"] is 0.0):
            for key in vs.keys():
                sent_sum[key] += float(vs[key])
                
            rating_sum += float(rating)
            num_ratings += 1
        
    for key in sent_sum.keys():
        sent_sum[key] = sent_sum[key] / num_ratings
        
    return (rating_sum/num_ratings, sent_sum)    
    
def pos_counts(tokens):
    verb_count, noun_count, adj_count, adv_count, modal_count = 0,0,0,0,0
    for token in list(tokens):
        if "MD" in token.tag_:
            modal_count += 1
        elif "JJ" in token.tag_:
            adj_count += 1
        elif "RB" in token.tag_:
            adv_count += 1
        elif "NOUN" in token.pos_:
            noun_count += 1
            
        elif "VERB" in token.pos_:    
            verb_count += 1
            
    return (verb_count, noun_count, adj_count, adv_count, modal_count)

def quantity_analysis(tokens):
    word_count = len(tokens)
    
    nc = list(tokens.noun_chunks)
    noun_phrase_count = len(nc)
    
    sents = list(tokens.sents)
    sentence_count = len(sents)
    
    return (word_count, noun_phrase_count, sentence_count)
    
def complexity_analysis(tokens, vendor):

    (verb_count, noun_count, adj_count, adv_count, modal_count) = pos_counts(tokens)

    (word_count, noun_phrase_count, sentence_count) = quantity_analysis(tokens)

    if len(tokens.text) is 0 or word_count is 0 or noun_phrase_count is 0 or sentence_count is 0:
        return (0,0,0,0,0)

    clause_count = 0
    for token in list(tokens):
        if ("VERB" in token.pos_):
            if token is token.head:
                clause_count += 1
            else:
                children = list(token.children)
                for child in children:
                    if "IN" in child.tag_ or "WDT" in child.tag_ or "WP" in child.tag_:
                        clause_count += 1
                        
    avg_num_of_clauses = clause_count * 1.0 / sentence_count
    avg_sentence_length = word_count*1.0 / sentence_count
    character_count = 0
    for token in list(tokens):
        character_count += len(token)
    avg_word_length = character_count*1.0/word_count

    words_in_nc_count = 0.0
    nc = list(tokens.noun_chunks)
    for noun_chunk in nc:
        words_in_nc_count += len(noun_chunk)
        
    avg_length_np = words_in_nc_count / noun_phrase_count
    
    punct_count = 0.0
    punct_dict = {}
    for token in tokens:
        if "PUNCT" in token.pos_:
            punct_count += 1
            if token.text in punct_dict:
                punct_dict[token.text] += 1
            else:
                punct_dict[token.text] = 1

    pausality = punct_count / sentence_count
    
    complexity = (avg_num_of_clauses, avg_sentence_length, avg_word_length, avg_length_np, pausality)
    
    return complexity
    
def uncertainty_analysis(tokens):
    uncertain_words = ["appear", "Appear",
    "seem", "Seem",
    "suggest", "Suggest",
    "indicat", "Indicat",
    "assum", "Assum",        
    "imply", "implie", "Imply", "Implie",
    "hope", "Hope", "hoping", "Hoping",
    "Think so", "think so"]
    
    txt = tokens.text
    uncertainty_count = 0
    for word in uncertain_words:
        uncertainty_count += txt.count(word)
        
    other_reference_words = [" he ", "He ", " she ", "She ",
        " him.", " him,", " him ", "himself",
        " her.", " her,", " her ", "herself",
        "It ", " it ", " it.", " it ", " itself ",
        " they", "They", "Them", "them",
        ]                
    
    other_reference_count = 0
    for word in other_reference_words:
        other_reference_count += txt.count(word)
        
    return (uncertainty_count, other_reference_count)
    
def nonimmediacy_analysis(tokens):
    
    self_ref = ["I ", " i ", " me.", " me!", " me,", " me ", "Me "]
    self_ref_count = 0
    for word in self_ref:
        self_ref_count += tokens.text.count(word)
        
    group_ref = ["We ", " we ", " us ", " us,", " us.", " Us ", " Us.", " us!", " Us!"]
    group_ref_count = 0
    for word in group_ref:
        group_ref_count += tokens.text.count(word)
    
    return (self_ref_count, group_ref_count)
    
def emotiveness_analysis(counts):
    (verb_count, noun_count, adj_count, adv_count, modal_count) = counts
    if (noun_count is 0 and verb_count is 0):
        return 0
    
    return (adj_count + adv_count*1.0) / (noun_count + verb_count)
    
def diversity_analysis(tokens):

    num_tokens = len(tokens)
    if num_tokens is 0:
        return (0,0)
    unique_tokens = frequencies(tokens)
    #print unique_tokens
    contents = get_content_words(tokens)
    unique_contents = frequencies(contents)
    
    if len(unique_contents.keys()) is 0 or len(unique_tokens.keys()) is 0:
        #print tokens
        return (0,0) 
    lex_div = num_tokens * 1.0 / len(unique_tokens.keys())
    con_div = len(contents) * 1.0/len(unique_contents.keys())
    return (lex_div, con_div)


"""        
def pos_tag(text):
    tags = nltk.pos_tag(tokens)
    return tags"""