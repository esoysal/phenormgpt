import re
import string
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

STOP_WORDS = [
         #"a", 
         "about", "again", "all", "almost", "also", "although", "always", "among", "an",
         "and", "another", "any", "are", "as", "at", "be", "because", "been", "before", "being", "between",
         "both", "but", "by", "can", "could", "did", "do", "does", "done", "due", "during", "each", "either",
         "enough", "especially", "etc", "for", "found", "from", "further", "had", "has", "have", "having",
         "here", "how", "however", #"i", 
         "if", "in", "into", "is", "it", "its", "itself", "just", "kg", "km",
         "made", "mainly", "make", "may", "mg", "might", "ml", "mm", "most", "mostly", "must", "nearly",
         "neither", "no", "nor", "obtained", "of", "often", "on", "or", "our", "overall", "perhaps", "pmid",
         "quite", "rather", "really", "regarding", "seem", "seen", "several", "should", "show", "showed",
         "shown", "shows", "significantly", "since", "so", "some", "such", "than", "that", "the", "their",
         "theirs", "them", "then", "there", "therefore", "these", "they", "this", "those", "through", "thus",
         "to", "upon", "use", "used", "using", "various", #"very", 
         "was", "we", "were", "what", "when", "which",
         "while", "with", "within", "would"]  # , "without"

UTF_PUNC = '‐‑‒–—―‖‘’‚‛“”„‟†‡•‣․‥…‧‰‱′″‴‵‶‷‸‹›※‼‽‾‿⁀⁁⁂⁃⁄⁅⁆⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁒⁓⁔⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞'
MATH_PUNC = '∀∁∂∃∄∅∆∇∈∉∊∋∌∍∎∏∐∑−∓∔∕∖∗∘∙√∛∜∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∱∲∳∴∵∶∷∸∹∺∻∼∽∾∿≀≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≐≑≒≓≔≕≖≗≘≙≚≛≜≝≞≟≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊌⊍⊎⊏⊐⊑⊒⊓⊔⊕⊖⊗⊘⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⊲⊳⊴⊵⊶⊷⊸⊹⊺⊻⊼⊽⊾⊿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿'
PUNCT = r'[-±+\t !@#$%^&*()_={}\[\]:;"\'<>,.?/–«»‘’‚‛′‵‘’‚‛“”„‟‹›;··〈〉‐‑‒–—―−⁃]+'
RE_PUNCT = re.compile(PUNCT)
PUNCTS = list(dict.fromkeys(string.punctuation).keys())
PUNCTS.extend(list('±–’«»‘‚‛‘’‚‛′‵“”„‟‹›;··.〈〉‐‑‒–—―−⁃'))

NOISE = '(?:\\b(?:%s|[0-9]+)\\b|%s|\\s+)' % ('|'.join(STOP_WORDS), PUNCT)
RE_NOISE = re.compile(NOISE, re.I)

stemmer = SnowballStemmer(language='english')

smart_case = str.lower

def stem(term, sort=False, lower=False, clean=False, stop_words=False):

    if clean:
        term = RE_PUNCT.sub(' ', term).strip()

    if lower:
        term = smart_case(term)

    tokens = word_tokenize(term)

    if stop_words:
        if lower:
            tokens = [token for token in tokens if token not in STOP_WORDS]
        else:
            tokens = [token for token in tokens if smart_case(token) not in STOP_WORDS]

    nterm = [stemmer.stem(token) for token in tokens if token not in PUNCTS]

    if sort:
        nterm = [smart_case(w) for w in nterm]
        nterm.sort()

    term = ' '.join(nterm)

    return term