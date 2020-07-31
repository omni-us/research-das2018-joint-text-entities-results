#!/usr/bin/env python3

import sys
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
        help='Whether to include confidences.')
    return parser


if __name__ == '__main__':
    cfg = get_parser().parse_args()

    pxml = pagexml.PageXML(cfg.xml())
    page_id = pxml.getValue('//@imageFilename').split('.')[0]

    for xreg in pxml.select('//_:TextRegion'):

        reg_id = page_id + '.' + pxml.getValue('@id', xreg)
        sys.stdout.write(reg_id+'\t')

        if cfg.with_conf:
            conf = min([float(pxml.getValue(e)) for e in pxml.select('.//_:TextEquiv/@conf', xreg)])
            sys.stdout.write(str(conf)+'\t')

        reg_text = ''
        for xword in pxml.select('.//_:Word', xreg):
            category = pxml.getValue('_:Property[@key="category"]/@value', xword)
            person = pxml.getValue('_:Property[@key="person"]/@value', xword)
            word_tag = ''
            if category != 'other' and person != 'none':
                word_tag = '<'+category+'-'+person+'/>'
            word_text = pxml.getTextEquiv(xword)
            reg_text += ' '+word_tag+word_text

        sys.stdout.write(reg_text[1:]+'\n')
