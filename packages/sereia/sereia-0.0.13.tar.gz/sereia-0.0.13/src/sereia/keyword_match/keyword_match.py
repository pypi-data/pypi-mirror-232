import json
import string
import re
from pprint import pprint as pp

class KeywordMatch:

    def __init__(self, table, value_filter={},schema_filter={}):
        self.__slots__ = ['table','schema_filter','value_filter']
        self.table = table
        # converted_value_filter = {}
        # for attribute, keywords in value_filter.items():
        #     for keyword in keywords:
        #         print('keyword, keywords')
        #         print(keyword, keywords)
        #         if isinstance(keyword, list):
        #             converted_value_filter[attribute] = frozenset(keyword)
        #         else:
        #             converted_value_filter[attribute] = keyword
        # print('schema filter: {} value filter: {}'.format(converted_schema_filter, converted_value_filter))
        self.schema_filter = frozenset({ (attribute,frozenset(keywords)) for attribute,keywords in schema_filter.items()})
        # self.value_filter = set([])
        # for attribute, keywords in converted_value_filter.items():
        #     print('building value filter')
        #     print(attribute, keywords)
        #     if isinstance(keywords, frozenset):
        #         self.value_filter.add((attribute, keywords))
        #     else:
        #         self.value_filter.add((attribute, frozenset(keywords)))
        # self.value_filter = frozenset(self.value_filter)
        value_filter_set = set([])
        for attribute,keywords in value_filter.items():
            # print(f'Attribute: {attribute} | Keywords: {keywords}')
            if isinstance(keywords, set):
                # print('is set')
                value_filter_set.add(
                    (attribute, frozenset(keywords)),
                )
            elif isinstance(keywords, frozenset):
                # print('is frozenset')
                value_filter_set.add(
                    (attribute, keywords),
                )
            elif isinstance(keywords[0], list):
                # print('is list')
                value_filter_set.add(
                    (attribute, frozenset([keywords[0]]))
                )
        # print('Value Filter Set: {}'.format(value_filter_set))
        # self.value_filter = frozenset(value_filter_set)#
        self.value_filter = frozenset({ (attribute,frozenset(keywords)) for attribute,keywords in value_filter.items()})
        # print(schema_filter, value_filter)

    def is_free(self):
        return len(self.schema_filter)==0 and len(self.value_filter)==0

    def schema_mappings(self):
        for attribute, keywords in self.schema_filter:
            yield (self.table,attribute,keywords)

    def value_mappings(self):
        for attribute, keywords in self.value_filter:
            yield (self.table,attribute,keywords)
    
    def has_value_mappings(self):
        return self.value_filter != frozenset({})

    def mappings(self):
        for attribute, keywords in self.schema_filter:
            yield ('s',self.table,attribute,keywords)
        for attribute, keywords in self.value_filter:
            yield ('v',self.table,attribute,keywords)

    def keywords(self,schema_only=False):
        for _, keywords in self.schema_filter:
            yield from keywords
        if not schema_only:
            for _, keywords in self.value_filter:
                for keyword in keywords:
                    if isinstance(keyword, frozenset):
                        for term in keyword:
                            yield term
                    else:
                        yield keyword

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        def str_filter(filter_type,fltr):
            if len(fltr) == 0:
                return ""
            
            str_repr = []
            
            for attribute, keywords in fltr:
                # print('Attribute: {} | Keywords: {}'.format(attribute, keywords))
                for keyword in keywords:
                    # print(keyword, type(keyword))
                    if isinstance(keyword, frozenset):
                        compound_keyword_segments = [
                            '{}'.format(
                                ','.join(keyword)
                            )
                        ]

                        compound_keyword_segments = ','.join(
                            compound_keyword_segments
                        )

                        str_repr.append(
                            (attribute, compound_keyword_segments),
                        )
                    else:
                        str_repr.append(
                            (
                                attribute,
                                keyword,
                            )
                        )

            return ".{}({})".format(
                filter_type,
                ','.join(
                    [
                        "{}{{{}}}".format(
                            attribute,
                            representation
                        ) for attribute, representation in str_repr
                    ]
                )
            )

        return "{}{}{}".format(self.table.upper(),str_filter('s',self.schema_filter),str_filter('v',self.value_filter))

    def __eq__(self, other):
        return (isinstance(other, KeywordMatch)
                and self.table == other.table
                #and set(self.keywords(schema_only=True)) == set(other.keywords(schema_only=True))
                and self.schema_filter == other.schema_filter
                and self.value_filter == other.value_filter)

    def has_default_mapping(self):
        schema_items = [attr for (attr, keywords) in self.schema_filter if attr == '*']
        value_items = [attr for (attr, keywords) in self.value_filter if attr == '*']

        return len(value_items) > 0 or len(schema_items) > 0

    def replace_default_mapping(self, attribute):
        schema_items = [attr for (attr, keywords) in self.schema_filter if attr == '*']
        value_items = [attr for (attr, keywords) in self.value_filter if attr == '*']

        if len(value_items) > 0:
            new_value_set = set({(attr, keywords) for attr, keywords in self.value_filter if attr != '*'})
            value = [keywords for (attr, keywords) in self.value_filter if attr == '*'][0]
            new_value_set.add((attribute, value))
            self.value_filter = frozenset(new_value_set)

        if len(schema_items) > 0:
            new_schema_set = set({(attr, keywords) for attr, keywords in self.schema_filter if attr != '*'})
            value = [keywords for (attr, keywords) in self.schema_filter if attr == '*'][0]
            new_schema_set.add((attribute, value))
            self.schema_filter = frozenset(new_schema_set)


    def has_same_attribute(self, other):
        all_equal_attributes = False
        attrib = set([attrib for (attrib,keywords) in self.value_filter])
        other_attrib = set([attrib for (attrib,keywords) in other.value_filter])

        if attrib != other_attrib:
            return False


        attrib = set([attrib for (attrib,keywords) in self.schema_filter])
        other_attrib = set([attrib for (attrib,keywords) in other.schema_filter])

        if attrib == other_attrib:
            all_equal_attributes=True

        return all_equal_attributes

    def __hash__(self):
        # return hash( (self.table,frozenset(self.keywords(schema_only=True)),self.value_filter) )
        return hash( (self.table,self.schema_filter,self.value_filter) )

    def to_json_serializable(self):

        def filter_object(fltr):
            filter_obj_list = []
            for attribute, keywords in fltr:
                filter_obj = {}
                filter_obj['attribute'] = attribute

                keywords_list = []

                for keyword in keywords:
                    if isinstance(keyword, frozenset):
                        keywords_list.append(list(keyword))
                        # for term in keyword:
                        #     keywords_list.append(term)
                    else:
                        keywords_list.append(keyword)
                
                filter_obj['keywords'] = keywords_list

                filter_obj_list.append(filter_obj)

            return filter_obj_list #[{'attribute':attribute,
                            #'keywords':list(keywords)} for attribute,keywords in fltr]
        
        # print(
        #     {'table':self.table,
        #         'schema_filter':filter_object(self.schema_filter),
        #         'value_filter':filter_object(self.value_filter),}
        # )

        return {'table':self.table,
                'schema_filter':filter_object(self.schema_filter),
                'value_filter':filter_object(self.value_filter),}

    def to_json(self):
        return json.dumps(self.to_json_serializable())

    @staticmethod
    def from_str(str_km):
        re_km = re.compile(r'([A-Z,_,1-9]+)(.*)')
        re_filters = re.compile(r'\.([vs])\(([^\)]*)\)')
        re_predicates = re.compile(r'([\w\*]*)\{([^\}]*)\}\,?')
        re_keywords = re.compile(r'(\w+)\,?')

        m_km=re_km.match(str_km)
        table = m_km.group(1).lower()
        schema_filter={}
        value_filter={}
        for filter_type,str_predicates in re_filters.findall(m_km.group(2)):

            if filter_type == 'v':
                predicates = value_filter
            else:
                predicates = schema_filter
            for attribute,str_keywords in re_predicates.findall(str_predicates):
                predicates[attribute]={key for key in re_keywords.findall(str_keywords)}
        return KeywordMatch(table,value_filter=value_filter,schema_filter=schema_filter,)

    @staticmethod
    def from_json_serializable(json_serializable):

        # print(json_serializable)

        def filter_dict(filter_obj):
            filter_dict_obj = {}
            
            for predicate in filter_obj:
                filter_dict_obj[predicate['attribute']] = []
                
                for keyword in predicate['keywords']:
                    if isinstance(keyword, list):
                        # print('is frozenset: {}'.format(keyword))
                        # print('')
                        filter_dict_obj[predicate['attribute']].append(frozenset(keyword))
                        # for term in keyword:
                        #     filter_dict_obj[predicate['attribute']].append(
                        #         term)
                    else:
                        filter_dict_obj[predicate['attribute']].append(keyword)
            
            # print('Filter dict object: {}'.format(filter_dict_obj))
            return filter_dict_obj
        
        # print('keyword match')
        # print(KeywordMatch(json_serializable['table'],
        #                     value_filter  = filter_dict(json_serializable['value_filter']),
        #                     schema_filter  = filter_dict(json_serializable['schema_filter'])).__repr__())
        # print('[FromJsonSerializable] Creating KeywordMatch with Value Filter: {}'.format(filter_dict(json_serializable['value_filter'])))

        return KeywordMatch(json_serializable['table'],
                            value_filter  = filter_dict(json_serializable['value_filter']),
                            schema_filter  = filter_dict(json_serializable['schema_filter']))
    @staticmethod
    def from_json(str_json):
        return KeywordMatch.from_json_serializable(json.loads(str_json))
