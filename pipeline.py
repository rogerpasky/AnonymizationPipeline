from ast import arg
from pyexpat import model
import anonymize
import formatters
import name_identifiers
import regex_identification
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, \
        help="File containing the original text with a context per line.")
    parser.add_argument("-m", "--model", type=str, \
        help="Path to the model that is going to be used", default="../models/iris_model")
    parser.add_argument("-t", "--type_of_model", choices=["spacy", "huggingface"], default="spacy", \
        help="The type of model that is going to be used for the NER recognition phase")
    parser.add_argument("-f", "--format", choices=["plain", "jsonl", "doccano"] , default="plain", \
        help="Format of the input file")
    parser.add_argument("-a", "--anonym_method", choices=["label", "random", "intelligent", "none"], default="none", \
        help="Anonymization technique that is going to be performed over the sensitive identified data")
    parser.add_argument("-o", "--output", type=str, \
        help="File to which the save action is performed", default="output.txt")

    args = parser.parse_args()
    
    input_path : str = args.input
    output_path : str = args.output
    model_path : str = args.model
    model_type : str = args.type_of_model
    input_format : str = args.format
    anonym_method : str = args.anonym_method

    print("Loading model")
    if model_type == "spacy":
        ner_model = name_identifiers.SpacyIdentifier(model_path)
    else:
        ner_model = name_identifiers.RoBERTaNameIdentifier(model_path)
    print("Finished loading model")
    
    print("Ingesting data")
    if input_format == "plain":
        ingester = formatters.PlainTextFormatter(input_path)
    elif input_format == "jsonl":
        ingester = formatters.ProdigyFormatter(input_path)
    else:
        ingester = formatters.DocannoFormatter(input_path)
    print("Finished ingesting data")

    regex_identifier = regex_identification.RegexIdentifier()
    
    print("Identifying sensitive data")
    for reg in ingester.registries:
        regex_identifier.identify_sensitive(reg)
        ner_model.identify_sensitive(reg)
    print("Finished identifying sensitive data")

    if anonym_method != "none":
        print("Instantiating anonymizer")
        if anonym_method == "label":
            anonymizer = anonymize.LabelAnonym()
        elif anonym_method == "random":
            anonymizer = anonymize.RandomAnonym()
        else: 
            anonymizer = anonymize.AllAnonym()
        print("Anonymizing data")
        ingester.anonymize_registries(anonymizer)
        print("Finished anonymizing data")


    print("Saving output")
    ingester.save(output_path)
    print("Finished saving output")


if __name__ == "__main__":
    main()