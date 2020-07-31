#!/usr/bin/env python3

import json
import pagexml
from jsonargparse import ArgumentParser, ActionPath


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('xml',
        action=ActionPath(mode='fr'),
        help='Page XML file to process.')
    parser.add_argument('--with_conf',
        type=bool,
        default=False,
        help='Whether to include confidences both at field level and document level.')
    parser.add_argument('--with_null',
        type=bool,
        default=False,
        help='Whether to include null values.')
    return parser


if __name__ == '__main__':
    cfg = get_parser().parse_args()

    pxml = pagexml.PageXML(cfg.xml())
    doc_conf = float('inf')
    records = []

    for nreg, reg in enumerate(pxml.select('//_:TextRegion')):

        record_dict = {}

        for partner in ['wife', 'husband']:
            partner_dict = {}
            xpath_partner = '_:Property[@key="person"]/@value="'+partner+'"'
            for detail in ['name', 'surname', 'state', 'occupation', 'location']:
                xpath_detail = '_:Property[@key="category"]/@value="'+detail+'"'
                xwords = pxml.select('.//_:Word['+xpath_partner+' and '+xpath_detail+']', reg)
                if xwords:
                    value = ' '.join(pxml.getTextEquiv(x) for x in xwords)
                    if cfg.with_conf:
                        conf = min([float(pxml.getValue('_:TextEquiv/@conf', x)) for x in xwords])
                        value = {'__conf__': conf, '__value__': value}
                        doc_conf = min(conf, doc_conf)
                    partner_dict[detail] = value
                elif cfg.with_null:
                    partner_dict[detail] = None
            for parent in ['mother', 'father']:
                parent_dict = {}
                xpath_parent = '_:Property[@key="person"]/@value="'+partner+'s_'+parent+'"'
                for detail in ['name', 'surname', 'occupation', 'location']:
                    xpath_detail = '_:Property[@key="category"]/@value="'+detail+'"'
                    xwords = pxml.select('.//_:Word['+xpath_parent+' and '+xpath_detail+']', reg)
                    if xwords:
                        value = ' '.join(pxml.getTextEquiv(x) for x in xwords)
                        if cfg.with_conf:
                            conf = min([float(pxml.getValue('_:TextEquiv/@conf', x)) for x in xwords])
                            value = {'__conf__': conf, '__value__': value}
                            doc_conf = min(conf, doc_conf)
                        parent_dict[detail] = value
                    elif cfg.with_null:
                        parent_dict[detail] = None
                if len(parent_dict) > 0:
                    partner_dict[parent] = parent_dict
            record_dict[partner] = partner_dict

        other_dict = {}
        xpath_other = '_:Property[@key="person"]/@value="other_person"'
        for detail in ['name', 'surname']:
            xpath_detail = '_:Property[@key="category"]/@value="'+detail+'"'
            xwords = pxml.select('.//_:Word['+xpath_other+' and '+xpath_detail+']', reg)
            if xwords:
                value = ' '.join(pxml.getTextEquiv(x) for x in xwords)
                if cfg.with_conf:
                    conf = min([float(pxml.getValue('_:TextEquiv/@conf', x)) for x in xwords])
                    value = {'__conf__': conf, '__value__': value}
                    doc_conf = min(conf, doc_conf)
                other_dict[detail] = value
            elif cfg.with_null:
                other_dict[detail] = None
        if len(other_dict) > 0:
            record_dict['other_person'] = other_dict

        records.append(record_dict)

    data = {'records': records}
    if cfg.with_conf:
        data = {'__conf__': doc_conf, '__value__': data}

    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
