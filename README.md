# Connections

###Description
 
Visits connections and people who may know in linked.

**Warning: Under development**

##Prerequisites
- Selenium
- Gecko Driver

### OSX installation

Installing Selenium

```bash
pip install selenium
```

Installng Gecko Driver

```bash
brew install geckodriver
```

### Windows installation
TODO


###Usage 
```python
from visit_connections import do_visit
exclude_list = ['john', 'paul']
profiles_viewed = do_visit('myusername@email.com','mypass', exclude_list)
print profiles_viewed 

Output:
{
	total_profiles_found: 245,
	total_viewed_profiles: 100	
} 
```
 
###TODO
 * Add feature to set options
 * Randomized viewing of profiles
 * Add a log
 * Use PhatomJS
 * Refactor as proper python module (class)
 
