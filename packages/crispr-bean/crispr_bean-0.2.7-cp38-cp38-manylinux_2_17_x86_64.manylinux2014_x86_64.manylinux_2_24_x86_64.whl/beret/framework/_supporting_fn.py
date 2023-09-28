from copy import deepcopy
from typing import List, Tuple
from tqdm.auto import tqdm
from .Edit import Edit, Allele
import pandas as pd
from ..annotate.translate_allele import CDS, RefBaseMismatchException


def filter_allele_by_pos(
    allele: Allele,
    pos_start: int = None, 
    pos_end: int = None,
    filter_rel_pos = True,
    ):
    '''
    Filter alleles based on position and return the filtered allele and
    number of filtered edits.
    '''
    filtered_edits = 0
    allele_filtered = deepcopy(allele)
    if not (pos_start is None and pos_end is None):
        if filter_rel_pos:
            for edit in allele.edits:
                if not (edit.rel_pos >= pos_start and edit.rel_pos < pos_end): 
                    filtered_edits += 1
                    allele_filtered.edits.remove(edit)
        else:
            for edit in allele.edits:
                if not (edit.pos >= pos_start and edit.pos < pos_end): 
                    filtered_edits += 1
                    allele_filtered.edits.remove(edit)

    else:
        print("No threshold specified") # TODO: warn
    return(allele_filtered, filtered_edits)

def filter_allele_by_base(
    allele: Allele,
    allowed_base_changes: List[Tuple] = None,
    allowed_ref_base: str = None, allowed_alt_base: str = None
):
    '''
    Filter alleles based on position and return the filtered allele and
    number of filtered edits.
    '''
    filtered_edits = 0
    if not (allowed_ref_base is None and allowed_alt_base is None) + (allowed_base_changes is None) == 1:
        print("No filters specified or misspecified filters.")
    elif not allowed_base_changes is None:
        for edit in allele.edits.copy():
            if not (edit.ref_base, edit.alt_base) in allowed_base_changes: 
                filtered_edits += 1
                allele.edits.remove(edit)
    elif not allowed_ref_base is None:
        for edit in allele.edits.copy():
            if edit.ref_base != allowed_ref_base: 
                filtered_edits += 1
                allele.edits.remove(edit)
            elif not allowed_alt_base is None and edit.alt_base != allowed_alt_base:
                filtered_edits += 1
                allele.edits.remove(edit)
    else:
        for edit in allele.edits.copy():
            if edit.alt_base != allowed_alt_base: 
                filtered_edits += 1
                allele.edits.remove(edit)
    return(allele, filtered_edits)

def get_aa_alleles(allele_str, include_synonymous = True):
    ldlr_cds = CDS()
    try:
        ldlr_cds.edit_allele(allele_str)
        ldlr_cds.get_aa_change(include_synonymous)
    except RefBaseMismatchException as e:
        print(e)
        return("ref mismatch")
    return ldlr_cds.get_aa_change(True)

def map_alleles_to_filtered(raw_allele_counts:pd.DataFrame, filtered_allele_counts: pd.DataFrame,
jaccard_threshold = 0.5):
    mapped_allele_counts = []#pd.DataFrame(columns=raw_allele_counts.columns)
    for guide, guide_raw_counts in tqdm(raw_allele_counts.groupby('guide'), desc = "Mapping alleles to closest filtered alleles"):
        guide_filtered_allele_counts = filtered_allele_counts.loc[filtered_allele_counts.guide == guide, :].set_index('allele')
        guide_filtered_alleles = guide_filtered_allele_counts.index.tolist()
        if len(guide_filtered_alleles) == 0: pass
        else:
            guide_raw_counts['allele_mapped'] = guide_raw_counts.allele.map(lambda allele: allele.map_to_closest(guide_filtered_alleles, jaccard_threshold = jaccard_threshold, merge_priority = guide_filtered_allele_counts.mean(axis=1, numeric_only=True)))
            # prioritize allele with most mean counts
            guide_raw_counts = guide_raw_counts.drop("allele", axis=1).rename(columns={"allele_mapped":"allele"})
            guide_raw_counts = guide_raw_counts.groupby(['guide', 'allele']).sum()
            mapped_allele_counts.append(guide_raw_counts)
    res = pd.concat(mapped_allele_counts).reset_index()
    res = res.loc[res.allele.map(str) != "", :]
    return(res)