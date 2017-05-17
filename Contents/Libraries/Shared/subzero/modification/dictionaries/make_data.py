# coding=utf-8

import re
import os
import pprint
from collections import OrderedDict

from bs4 import BeautifulSoup

TEMPLATE = """\
import re
from collections import OrderedDict
data = """

TEMPLATE_END = """\

for lang, grps in data.iteritems():
    for grp in grps.iterkeys():
        if data[lang][grp]["pattern"]:
            data[lang][grp]["pattern"] = re.compile(data[lang][grp]["pattern"])
"""


SZ_FIX_DATA = {
    "eng": {
        "PartialWordsAlways": {
            u"°x°": u"%",
            u"compiete": u"complete",
        },
        "WholeWords": {
            u"I'11": u"I'll",
            u"Tun": u"Run",
            u"pan'": u"part",
            u"al'": u"at",
            u"a re": u"are",
            u"Mr": u"Mr.",
            u"wail'": u"wait",
        }
    }
}

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    xml_dir = os.path.join(cur_dir, "xml")
    file_list = os.listdir(xml_dir)

    data = {}

    for fn in file_list:
        if fn.endswith("_OCRFixReplaceList.xml"):
            lang = fn.split("_")[0]
            soup = BeautifulSoup(open(os.path.join(xml_dir, fn)), "xml")

            fetch_data = (
                    # group, item_name, pattern
                    ("WholeLines", "Line", None),
                    ("WholeWords", "Word", lambda d: (ur"(?um)\b(?:" + u"|".join([re.escape(k) for k in d.keys()])
                                                      + ur')\b') if d else None),
                    ("PartialWordsAlways", "WordPart", None),
                    ("PartialLines", "LinePart", lambda d: (ur"(?um)(?:(?<=\s)|(?<=^)|(?<=\b))(?:" +
                                                            u"|".join([re.escape(k) for k in d.keys()]) +
                                                            ur")(?:(?=\s)|(?=$)|(?=\b))") if d else None),
                    ("BeginLines", "Beginning", lambda d: (ur"(?um)^(?:"+u"|".join([re.escape(k) for k in d.keys()])
                                                           + ur')') if d else None),
                    ("EndLines", "Ending", lambda d: (ur"(?um)(?:" + u"|".join([re.escape(k) for k in d.keys()]) +
                                                      ur")$") if d else None,),
            )

            data[lang] = dict((grp, {"data": OrderedDict(), "pattern": None}) for grp, item_name, pattern in fetch_data)

            for grp, item_name, pattern in fetch_data:
                for grp_data in soup.find_all(grp):
                    for line in grp_data.find_all(item_name):
                        data[lang][grp]["data"][line["from"]] = line["to"]

                # add our own dictionaries
                if lang in SZ_FIX_DATA and grp in SZ_FIX_DATA[lang]:
                    data[lang][grp]["data"].update(SZ_FIX_DATA[lang][grp])

                if pattern:
                    data[lang][grp]["pattern"] = pattern(data[lang][grp]["data"])

    f = open(os.path.join(cur_dir, "data.py"), "w+")
    f.write(TEMPLATE)
    f.write(pprint.pformat(data, width=1))
    f.write(TEMPLATE_END)
    f.close()
