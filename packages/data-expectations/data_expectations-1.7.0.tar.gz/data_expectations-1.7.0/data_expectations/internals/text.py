# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

try:
    # added 3.9
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(1)

SPECIAL_REGEX_CHARS = {ch: "\\" + ch for ch in ".^$*+?{}[]|()\\"}


@cache
def sql_like_to_regex(fragment):
    """Create a RegEx to test a SQL LIKE condition"""
    safe_fragment = "".join([SPECIAL_REGEX_CHARS.get(ch, ch) for ch in fragment])
    return re.compile("^" + safe_fragment.replace("%", ".*?").replace("_", ".") + "$")
