#!/usr/bin/env python3

import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import sqlite3
from utils import utils


def check_for_other_genotypes(variant: str, genotype: str, database: sqlite3.Connection, logs: dict):
    utils.warn_about_no_genotype(variant, genotype)
    df_logs = pd.read_sql(f'''SELECT * FROM clinical_ann_alleles 
        INNER JOIN clinical_annotations 
        ON clinical_ann_alleles.Clinical_Annotation_ID = clinical_annotations.Clinical_Annotation_ID
        WHERE (clinical_annotations.Variant_Haplotypes LIKE "%{variant},%"
        OR clinical_annotations.Variant_Haplotypes LIKE "%{variant}")''' , database)
    df_logs = utils.drop_duplicated_columns(df_logs)
    if not df_logs.empty:
        utils.warn_about_other_genotypes(variant)
        df_logs = utils.split_fields(df=df_logs, fields=["Gene", "Drug(s)", "Phenotype(s)"], split_char=";")
        try:
            genes = utils.flatten_list(df_logs["Gene"].tolist())
            gene = utils.most_frequent(genes)
        except TypeError:
            gene = variant
        if gene in logs:
            logs[gene][variant] = utils.df_to_json(df_logs)
        else:
            logs[gene] = {variant: utils.df_to_json(df_logs)}       


def get_clinical_annotation(queries: dict, database: sqlite3.Connection) -> dict:
    output = dict()
    logs = dict()
    for variant, genotype in queries.items():
        df = pd.read_sql(f'''SELECT * FROM clinical_ann_alleles 
            INNER JOIN clinical_annotations 
            ON clinical_ann_alleles.Clinical_Annotation_ID = clinical_annotations.Clinical_Annotation_ID
            WHERE (clinical_annotations.Variant_Haplotypes LIKE "%{variant},%"
            OR clinical_annotations.Variant_Haplotypes LIKE "%{variant}")
            AND (clinical_ann_alleles.Genotype_Allele LIKE "{genotype}"
            OR (clinical_ann_alleles.Genotype_Allele LIKE "%+%"
            AND (clinical_ann_alleles.Genotype_Allele LIKE "%+ {genotype}"
            OR clinical_ann_alleles.Genotype_Allele LIKE "{genotype} +%")))''', database)
        # df to json
        df = utils.drop_duplicated_columns(df)
        if df.empty:
            check_for_other_genotypes(variant, genotype, database, logs)
        else:
            df["PMID"] = None
            for index, row in df.iterrows():
                clinical_annotation_id = row["Clinical_Annotation_ID"]
                df_pmid = pd.read_sql(f'''SELECT PMID FROM clinical_ann_evidence 
                        WHERE Clinical_Annotation_ID = "{clinical_annotation_id}"''', database)
                pmids = df_pmid["PMID"].tolist()
                pmids = [x for x in pmids if str(x) != 'nan']
                pmids = [int(ele) for ele in pmids]
                df["PMID"][index] = pmids
            df = utils.split_fields(df=df, fields=["Gene", "Drug(s)", "Phenotype(s)"], split_char=";")
            try:
                genes = utils.flatten_list(df["Gene"].tolist())
                gene = utils.most_frequent(genes)
            except TypeError:
                gene = variant
            # add report genotype
            utils.add_report_genotype(df, gene, variant, genotype)
            if gene in output:
                output[gene][variant] = utils.df_to_json(df)
            else:
                output[gene] = {variant: utils.df_to_json(df)}
    return output, logs


def main():
    parser = argparse.ArgumentParser(description='Get clinical annotation from PharmGKB')
    parser.add_argument('--queries', type=str, required=True, help='Json file with queries to db')
    parser.add_argument('--output-filename', type=str, required=True, help='Output filename')
    args = parser.parse_args()

    # load queries
    queries = utils.load_json(args.queries)

    # connect to database
    database = utils.connect_to_database("clinical.db")

    # get variant annotation
    output, logs = get_clinical_annotation(queries, database)

    # save output
    utils.save_json(output, args.output_filename)

    # save logs
    utils.save_json(logs, "variants_with_unknown_genotype.json")


if __name__ == '__main__':
    main()
