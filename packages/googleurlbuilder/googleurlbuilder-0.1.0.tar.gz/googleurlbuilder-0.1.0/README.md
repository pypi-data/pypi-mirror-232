# Google URL Builder.

Simple pure Python Google URL generator based on 
[Google advanced search](https://www.google.com/advanced_search).

### Why?

In some development cases, you may need to generate Google search URLs without the wish 
to request Google(.com).

<ins>In example :</ins>
-   for displaying/providing those URLs directly to the end user.
-   to have more control over what your code makes.


### Package principles.

-   Pure Python → No more depedencies needed.
-   Strong typing.

## Examples.

### Import package.


```python
from googleurlbuilder import (
    GoogleURL,
    SearchFilters,
    parameters as pr, # Aliases are optionnal.
    # Query parameters.
    operators as op,
    # Operators over query parameters.
    filters as ft,
    # Filters.
)
```

### Simple use case.


```python
url = GoogleURL((pr.Words(["search", "google"]) + pr.ExactPhrases(["google search"])))

print(url.compute_url())
```

    https://google.com/search?q=%28%28search+google%29+%22google+search%22%29
    

### Use filters.


```python
url = GoogleURL(
    query=pr.Words(["search", "google"]),
    filters=SearchFilters(language=ft.Languages.French),
    tld="fr",
)

print(url.compute_url())
```

    https://google.fr/search?lr=lang_fr&q=%28search+google%29
    

### Use operators over search parameters.


```python
query = op.Or(pr.Words(["search"]), pr.ExactPhrases(["google"]))
print(query)
query = pr.Words(["search"]) | pr.ExactPhrases(["google"])  # equivalent.
print(query)
```

    (search OR "google")
    (search OR "google")
    
