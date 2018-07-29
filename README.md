# thermohw

Homework assignment converter from Jupyter Notebooks to PDF

This package installs a CLI script to convert Jupyter Notebook homework
assignments to PDF (with and without solutions) and a set of Notebooks
(with and without solutions).

Given a directory structure such as
```
.
├── homework
|   ├── homework-1
│   │   ├── homework-1-1.ipynb
│   │   ├── homework-1-2.ipynb
│   │   ├── homework-1-3.ipynb
│   │   ├── homework-1-4.ipynb
│   │   ├── homework-1-5.ipynb
│   │   ├── homework-1-6.ipynb
|   ├── homework-2
│   │   ├── homework-2-1.ipynb
│   │   ├── homework-2-2.ipynb
│   │   ├── homework-2-3.ipynb
│   │   ├── homework-2-4.ipynb
...
```
running

```bash
convert_thermo_hw --hw 1
```
will convert all of the `.ipynb` files in the`homework-1` directory. You can also specify which problems should be converted by the `problems` argument, which takes a list of integers
```bash
convert_thermo_hw --hw 2 --problems 1 3 4
```
would convert problems 1, 3, and 4 in `homework-2`.

The output files are placed in a directory called `output` in the `homework-N` directory.
