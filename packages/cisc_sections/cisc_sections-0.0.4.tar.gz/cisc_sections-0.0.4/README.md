<!--- Heading --->
<div align="center">
  <h1>CISC-Sections</h1>
  <p>
    Python library to lookup structural steel sections from CISC manual. 
  </p>
<h4>
    <a href="https://github.com/rpakishore/steelsections-cisc/">View Demo</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/steelsections-cisc">Documentation</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/steelsections-cisc/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/steelsections-cisc/issues/">Request Feature</a>
  </h4>
</div>
<br />

<!-- Badges -->
[![tests](https://github.com/rpakishore/steelsections-cisc/actions/workflows/tests.yml/badge.svg)](https://github.com/rpakishore/steelsections-cisc/actions/workflows/tests.yml)

<!-- Table of Contents -->
<h2>Table of Contents</h2>

- [1. About the Project](#1-about-the-project)
  - [1.1. Features](#11-features)
  - [1.2. Prerequisites](#12-prerequisites)
  - [1.3. Dependencies](#13-dependencies)
  - [1.4. Installation](#14-installation)
- [2. Usage](#2-usage)
- [3. Roadmap](#3-roadmap)
- [4. License](#4-license)
- [5. Contact](#5-contact)

<!-- About the Project -->
## 1. About the Project

<!-- Features -->
### 1.1. Features

- Can lookup section properties of W, HSS, C, L and much more based on canadian CISC manual.
- Uses [forallpeople](https://github.com/connorferster/forallpeople) to return units-aware results.
- Prelim. filters to narrow down the sections returned.

<!-- Prerequisites -->
### 1.2. Prerequisites

### 1.3. Dependencies

The project uses the following dependencies

```toml
pandas>=1.5.2
forallpeople>=2.6.3
```

<!-- Installation -->
### 1.4. Installation

Install from pip

```bash
pip install cisc_sections
```

Alternatively, compile it locally using the flit

```bash
git clone https://github.com/rpakishore/steelsections-cisc.git
cd steelsections-cisc
python -m pip install flit
flit install
```
<!-- Usage -->
## 2. Usage

The most basic use is just to import the library:

```python
import cisc_sections as steel
```

Directly obtain section properties for use elsewhere

```python
from cisc_sections import Sections
sections = Sections()

# Get W150x37 section
W150x37 = sections.W.W150x37
print(W150x37) # Instance of SteelSection class for W150x37 section

# Get Area
W150x37.A.value # 4750.000 mm²

print(W150x37.Sx * W150x37.A) # 1306250000.000 mm⁵
```
<!-- Roadmap -->
## 3. Roadmap

- [ ] Add typical steel $F_y$ for each section
- [ ] Section capacity calculator

<!-- License -->
## 4. License

Distributed under the no License. See LICENSE for more information.

<!-- Contact -->
## 5. Contact

Arun Kishore - [@rpakishore](mailto:pypi@rpakishore.co.in)

Project Link: [https://github.com/rpakishore/](https://github.com/rpakishore/)