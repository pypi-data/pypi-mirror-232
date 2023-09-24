# mathmini-pip
Sample math library containing add and sub functions

# Installation
```bash
pip install mathmini
```

# Usage
```bash
python3 -m mathmini add 10 5
python3 -m mathmini sub 10 5
```

```python
import mathmini

print(mathmini.add(10, 5))
print(mathmini.sub(10, 5))
```

# Release and Publish
1. Update `version` in `setup.cfg`
2. Commit changes
3. Run `git tag v1.0.0`
4. Run `git push origin v1.0.0`
