"""
file containing code that related to n-level extraction of address
"""

import re
from copy import deepcopy
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

import pandas as pd
from flashtext import KeywordProcessor
from preprocessing_pgp.address.const import (
    ADDRESS_ADDITIONAL_NON_BOUNDARY,
    ADVANCED_METHODS,
    LOCATION_ENRICH_DICT,
    METHOD_REFER_DICT,
    NON_STREET_PATTERNS,
)
from preprocessing_pgp.address.utils import (
    NonWordBoundaries,
    create_dependent_query,
    flatten_list,
    remove_substr,
)
from preprocessing_pgp.name.preprocess import remove_duplicated_name
from tqdm import tqdm

tqdm.pandas()


class LevelExtractor:
    """
    Class contains information of extract level and functions to process on each level

    * Level 1: City, Countryside
    * Level 2: District
    * Level 3: Ward
    """

    def __init__(self) -> None:
        self.avail_levels = METHOD_REFER_DICT.keys()
        self.avail_methods = flatten_list(METHOD_REFER_DICT.values())
        self.keyword_refer_dict = dict(
            zip(
                self.avail_methods,
                [
                    self._generate_keyword_processor(method)
                    for method in self.avail_methods
                ],
            )
        )
        self.advanced_keyword_regex_dict = dict(
            zip(
                ADVANCED_METHODS,
                [
                    "$|".join(LOCATION_ENRICH_DICT[method].unique()) + "$"
                    for method in ADVANCED_METHODS
                ],
            )
        )

    def _get_level_methods(self, level) -> List:
        """
        _summary_

        Parameters
        ----------
        level : _type_
            _description_

        Returns
        -------
        List
            _description_
        """
        return METHOD_REFER_DICT[level]

    def _get_level_keywords(self, level: int = 1) -> List:
        """
        Function to get all keywords of each specific level

        Parameters
        ----------
        level : int, optional
            The number of level (1-3) to generate method keywords, by default 1

        Returns
        -------
            The output list of keywords for each of the level's methods
        """
        level_kws = []
        for method in self._get_level_methods(level):
            method_kw = self._generate_keyword_processor(method)
            level_kws.append(method_kw)

        return level_kws

    def _generate_keyword_processor(self, method: str) -> KeywordProcessor:
        """
        Function to generate `KeywordProcessor` object
        to the specific `method`
        using the generated dictionary of keywords

        Parameters
        ----------
        method : str
            The method string refer to the dictionary column name

        Returns
        -------
        KeywordProcessor
            `KeywordProcessor` object that contains all the keywords of the method
        """
        unique_method_kws = LOCATION_ENRICH_DICT[method].unique().tolist()

        keyword_processor = KeywordProcessor(case_sensitive=True)
        keyword_processor.add_keywords_from_list(unique_method_kws)
        keyword_processor.set_non_word_boundaries(
            NonWordBoundaries(
                str.isalpha,
                str.isdigit,
                lambda w: w in ADDRESS_ADDITIONAL_NON_BOUNDARY,
            )
        )

        return keyword_processor

    def _get_match_keyword(
        self, query: str, kw_processor: KeywordProcessor
    ) -> Tuple[str, Tuple[int, int]]:
        """
        Function to get the last keyword found in `query` string

        Parameters
        ----------
        query : str
            The input query string containing the address
        kw_processor : KeywordProcessor
            The keyword processor for specific method in dictionary (norm, abbrev, ...)

        Returns
        -------
        Tuple[str, Tuple[int, int]]
            Last match keyword found in query and range pairs, if not found return None
        """

        try:
            found_keyword, start_pos, end_pos = kw_processor.extract_keywords(query, span_info=True)[-1]
            return found_keyword, (start_pos, end_pos)
        except Exception as _:
            return None, (None, None)

    def extract_all_levels(self, address: str) -> Tuple[Dict, str]:
        """
        Traverse through all possible level from lowest to highest
        to check and find `best pattern` in each level
        and `return` as a `dictionary of pattern` found at each level with `remaining address`

        Parameters
        ----------
        address : str
            The unified address that has been `lowered` and `unidecode`

        Returns
        -------
        Tuple[Dict, str]
            The output contains:
            * a dictionary of `pattern` found at each level
            * `remained address`
            * a dictionary of `best pattern` found at each level
        """

        remained_address = deepcopy(address)
        found_patterns = dict(zip(self.avail_levels, [None] * len(self.avail_levels)))
        best_patterns = deepcopy(found_patterns)

        dependents = []
        for level in self.avail_levels:
            (
                level_pattern,
                remained_address,
                level_method,
                level_best_pattern,
            ) = self._extract_by_level(remained_address, level, *dependents)

            found_patterns[level] = level_pattern
            best_patterns[level] = level_best_pattern
            dependents.append((level_pattern, level_method))

        # * Relation filtering for level 1, 2
        if best_patterns[1] is None:
            if best_patterns[2] is None:
                best_patterns[1] = self.__relation_filtering(
                    "lv1",
                    (best_patterns[3], "lv3"),
                )
                best_patterns[2] = self.__relation_filtering(
                    "lv2",
                    (best_patterns[3], "lv3"),
                    (best_patterns[1], "lv1"),
                )
            else:
                best_patterns[1] = self.__relation_filtering(
                    "lv1",
                    (best_patterns[2], "lv2"),
                    (best_patterns[3], "lv3"),
                )
        if best_patterns[2] is None:
            if best_patterns[1] is not None:
                best_patterns[2] = self.__relation_filtering(
                    "lv2",
                    (best_patterns[1], "lv1"),
                    (best_patterns[3], "lv3"),
                )

        # * Remove non-street characters
        remained_address = re.sub(
            r"(?i)[^\u0030-\u0039\u0061-\u007A\u00C0-\u1EF8 /-]",
            " ",
            remained_address,
        )
        remained_address = re.sub(r"\s+", " ", remained_address).strip()
        remained_address = remove_duplicated_name(remained_address)
        if (found_patterns[1] is not None) and (
            address.find(found_patterns[1]) == 0
        ):  # The address is in reversed
            remained_address = self._get_best_street(
                address, remained_address, in_reversed=True
            )
        else:
            remained_address = self._get_best_street(
                address, remained_address, in_reversed=False
            )
        for level in self.avail_levels:
            if None in [best_patterns[level], found_patterns[level]]:
                continue
            remained_address = remove_substr(remained_address, found_patterns[level])
        remained_address = re.sub(r"\s+", " ", remained_address).strip()

        return found_patterns, remained_address, best_patterns

    def __relation_filtering(self, level: str, *dependents) -> str:
        """
        Relation filtering to track back for higher level
        """
        dep_query = self.__make_dependent_query(*dependents)
        if dep_query == "":
            return None

        pattern_result = LOCATION_ENRICH_DICT.query(dep_query)[level].unique()

        if pattern_result.shape[0] != 1:
            return None

        return pattern_result[0]

    def __is_query_exist(self, query: str) -> bool:
        """
        Helper function to check whether the query is possibly found in location data
        """
        n_result = LOCATION_ENRICH_DICT.query(query).shape[0]

        return n_result > 0

    def __make_dependent_query(self, *dependents) -> str:
        """
        Helper to make search query from dependents
        """
        query = ""
        # Making dependent queries
        if len(dependents) > 0:
            dependent_queries = []
            for d_term, d_method in dependents:
                if d_term is not None:
                    term_query = f'{d_method} == "{d_term}"'
                    dependent_queries.append(term_query)

            query = create_dependent_query(*dependent_queries)

        return query

    def __is_correct_dependent(self, *dependents) -> bool:
        """
        Helper function to check whether the dependencies are all correct
        """
        query = self.__make_dependent_query(*dependents)

        if query != "":
            return self.__is_query_exist(query)

        return False

    def _extract_by_level(
        self, address: str, level: int, *dependents
    ) -> Tuple[str, str, str, str]:
        """
        Extract address with list of `method`
        at the specific `level`
        to find the best matched pattern

        Parameters
        ----------
        address : str
            The unified address that has been `titled`
        level : int
            The level which is currently traversed from

        Returns
        -------
        Tuple[str, str, str, str]
            The output contains:
            * `pattern` found within specific level
            * `remained address`
            * `method` which retrieved the pattern
            * `best pattern` unified by `pattern`
        """
        level_methods = self._get_level_methods(level)

        # Advanced methods
        for method in ADVANCED_METHODS:
            pattern_found, remained_address = self._extract_by_advanced_method(
                address, method
            )
            if (pattern_found is not None) and (len(pattern_found) > 0):
                if self.__is_correct_dependent(*dependents, (pattern_found, method)):
                    query = self.__make_dependent_query(
                        *dependents, (pattern_found, method)
                    )

                    best_pattern = self.__trace_best_match(query, f"lv{level}")

                    if level == 1:
                        return (
                            pattern_found,
                            remained_address + " " + pattern_found,
                            method,
                            best_pattern,
                        )
                    return (pattern_found, remained_address, method, best_pattern)

        found_patterns = {}

        for method in level_methods:
            pattern, position = self._extract_by_method(address, method)
            if pattern is not None:
                found_patterns[pattern] = {
                    'position': position,
                    'method': method
                }
            # if remained_address:
            #     print(remained_address)

            # # Found something then return
            # if (pattern_found is not None) and (len(pattern_found) > 0):
            #     if self.__is_correct_dependent(*dependents, (pattern_found, method)):
            #         best_pattern = self.__trace_match_pattern(
            #             pattern_found, method, *dependents
            #         )

            #         return (
            #             pattern_found,
            #             remained_address,
            #             method,
            #             best_pattern,
            #         )

        # ALL found patterns
        found_patterns = dict(sorted(found_patterns.items(), key=lambda item: item[1]['position'], reverse=True))
        try:
            final_pattern = list(found_patterns.keys())[0]
            final_method = list(found_patterns.values())[0]['method']

            if (final_pattern is not None) and (len(final_pattern) > 0):
                if self.__is_correct_dependent(*dependents, (final_pattern, final_method)):
                    best_pattern = self.__trace_match_pattern(
                        final_pattern, final_method, *dependents
                    )

                    remained_address = remove_substr(address, final_pattern)

                    return (
                        final_pattern,
                        remained_address,
                        final_method,
                        best_pattern,
                    )
            return None, address, None, None

        except IndexError as _:
            return None, address, None, None

    def _extract_by_advanced_method(self, address: str, method: str) -> Tuple[str, str]:
        """
        Extract the address with keywords in advanced methods

        Parameters
        ----------
        address : str
            The unified addressed that has been `titled`

        Returns
        -------
        Tuple[str, str]
            The output contains:
            * `pattern` found within specific method
            * `remained address`
        """
        try:
            match_pattern = re.findall(
                self.advanced_keyword_regex_dict[method], address
            )[-1]
        except:
            match_pattern = None

        remained_address = remove_substr(address, match_pattern)

        return match_pattern, remained_address

    def _extract_by_method(self, address: str, method: str) -> Tuple[str, Tuple[int, int]]:
        """
        Extract the address with `keywords` of the specific method

        Parameters
        ----------
        address : str
            The unified address that has been `titled`
        method : str
            The method of level which is currently being explored

        Returns
        -------
        Tuple[str, Tuple[int, int]]
            The output contains:
            * `pattern` found within specific method
            * The position of the patterns
        """
        method_kw = self.keyword_refer_dict[method]
        match_pattern, pos = self._get_match_keyword(address, method_kw)
        # remained_address = remove_substr(address, match_pattern)

        return match_pattern, pos

    def __trace_match_pattern(self, pattern: str, method: str, *dependents) -> str:
        """
        Helper function to trace back best pattern found
        """
        query = self.__make_dependent_query(*dependents, (pattern, method))

        if not self.__is_query_exist(query):
            return None

        level_col = method[:3]

        best_match = self.__trace_best_match(query, level_col)

        return best_match

    def __trace_best_match(self, query: str, level_col: str) -> str:
        """
        Helper to get the best match consist of:

        1. Exist
        2. Unique found
        """
        found_terms = LOCATION_ENRICH_DICT.query(query)[level_col].unique()

        n_found = found_terms.shape[0]
        if n_found == 0 or n_found > 1:
            return None

        return found_terms[0]

    def _clean_street(self, street: str) -> str:
        """
        Clean the street to remove redundant street patterns

        Parameters
        ----------
        street : str
            The street to clean

        Returns
        -------
        str
            Cleaned street with no redundant patterns
        """
        pattern = r"(?i)\b(?:{})(?=\s|$)".format(
            "|".join(map(re.escape, NON_STREET_PATTERNS))
        )

        clean_street = re.sub(pattern, " ", street)
        clean_street = re.sub(r"\s+", " ", clean_street).strip()

        return clean_street

    def _get_best_street(
        self, clean_raw_address: str, remaining_address: str, in_reversed: bool = False
    ) -> str:
        """
        Clean the street by doing lcs with the clean street

        Parameters
        ----------
        clean_raw_address : str
            The full raw address in clean format
        remaining_address : str
            The remaining address after extraction

        Returns
        -------
        str
            The final clean street
        """

        lcs_match = SequenceMatcher(
            None, clean_raw_address, remaining_address
        ).find_longest_match()

        if lcs_match.a != 0 and not in_reversed:
            clean_address = ""
        else:
            clean_address = clean_raw_address[
                lcs_match.a : (lcs_match.a + lcs_match.size)
            ]

        clean_address = self._clean_street(clean_address)

        return clean_address


def extract_vi_address_by_level(data: pd.DataFrame, address_col: str) -> pd.DataFrame:
    """
    Function to extract vietnamese address into each specific level found by pattern

    Parameters
    ----------
    data : pd.DataFrame
        Raw data containing the address
    address_col : str
        The raw address column that need cleansing and unifying

    Returns
    -------
    pd.DataFrame
        Final data with new columns:

        * `level_1`: city, countryside found
        * `best_level_1`: beautified city, countryside found
        * `level_2`: district found
        * `best_level_2`: beautified district found
        * `level_3`: ward found
        * `best_level_3`: beautified ward found
        * `remained_address`: the remaining in the address
    """

    extractor = LevelExtractor()

    extracted_data: pd.DataFrame = data

    extracted_results = extracted_data[address_col].progress_apply(
        extractor.extract_all_levels
    )

    for level in extractor.avail_levels:
        extracted_data[f"level_{level}"] = [
            result[0][level] for result in extracted_results
        ]

        extracted_data[f"best_level_{level}"] = [
            result[-1][level] for result in extracted_results
        ]

    extracted_data["remained_address"] = [result[1] for result in extracted_results]

    return extracted_data
