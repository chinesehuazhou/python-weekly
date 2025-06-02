# Python Trending Weekly #104: Python Considering Adding Virtual Threads?

Hello, I'm Python Cat. Welcome to the Python Trending Weekly, a weekly newsletter about Python, AI and general programming techniques, with the majority links in English and a small portion in Chinese. 

## [🦄Articles & Tutorials](https://xiaobot.net/p/python_weekly)

1、[Pyrefly vs. ty: Comparing Python's Two New Rust-Based Type Checkers](https://blog.edward-li.com/tech/comparing-pyrefly-vs-ty/)

Both Meta's Pyrefly and Astral's ty are Python type checking tools developed based on Rust, and they both appeared at this year's PyCon Typing Summit. The article introduces their differences in development background, design philosophy, technical features and performance.

2、[Single process, multiple interpreters, no GIL contention - pre-Python3.12](https://basisrobotics.tech/2025/05/26/python/)

How to implement single-process multi-interpreter execution in Python versions before 3.12? The article introduces using dlopen and dynamic library loading mechanisms to bypass Python's single interpreter limitation. This approach allows the robotics framework Basis to run multiple Python instances in the same process space while avoiding GIL contention, providing an innovative architectural solution for high-performance robotics systems.

3、[Why, in 2025, do we still need a 3rd party app to write a REST API with Django?](https://www.djangoproject.com/weblog/2025/may/22/why-need-3rd-party-app-rest-api-with-django/)

This article from the official Django blog raises a question: Do we really need third-party libraries to build REST APIs with Django? It introduces how to use Django's built-in generic class views and form system to implement complete CRUD REST API functionality with less than 100 lines of code.

4、[Introducing Pyrefly: A new type checker and IDE experience for Python](https://engineering.fb.com/2025/05/15/developer-tools/introducing-pyrefly-a-new-type-checker-and-ide-experience-for-python/)

Meta officially announced the alpha version of Pyrefly, which can perform type checking at a speed of 1.8 million lines of code per second, supporting IDE-first development experience and automatic type inference. The article explains why it was developed to replace Pyre, the principles behind it, and future development plans.

5、[Python Pandas Ditches NumPy for Speedier PyArrow](https://thenewstack.io/python-pandas-ditches-numpy-for-speedier-pyarrow/)

Pandas is about to release version 3.0, which will use PyArrow to replace NumPy as the default engine for handling columnar data loading and reading. PyArrow provides columnar storage, supports Copy on Write mode, and has significant advantages in memory usage and reading speed.

6、[Tiny Agents in Python: an MCP-powered agent in ~70 lines of code](https://huggingface.co/blog/python-tiny-agents)

Hugging Face released "Tiny Agents", which can enable large language models to call external tools and APIs through the MCP protocol, thereby achieving more powerful functionality. The article demonstrates its usage and powerful capabilities.

7、[Narwhals: Unified DataFrame Functions for pandas, Polars, and PySpark](https://codecut.ai/unified-dataframe-functions-pandas-polars-pyspark/)

Narwhals is a lightweight compatibility layer that unifies functions from mainstream DataFrame libraries like pandas, Polars, and PySpark, avoiding the complexity of writing separate code for each library and improving code portability and reusability.

8、[DumPy: NumPy except it's OK if you're dum](https://dynomight.net/dumpy/)

The author proposes redesigning NumPy with loop and indexing syntax, solving the complexity of high-dimensional array operations by compiling loop syntax into vectorized operations. DumPy implements automatic vectorization based on JAX's vmap, allowing intuitive loop syntax to achieve GPU-accelerated performance, significantly reducing the cognitive burden of multi-dimensional array programming.

9、[Beyond Query Optimization: Aurora Postgres Connection Pooling with SQLAlchemy & RDSProxy](https://eng.lyft.com/beyond-query-optimization-aurora-postgres-connection-pooling-with-sqlalchemy-rdsproxy-200db7f562d7)

Lyft's engineering team shares their practical experience migrating from application-level connection pooling to AWS RDSProxy proxy connection pooling. It details the importance of connection pooling, SQLAlchemy configuration methods, and how RDSProxy solves the problem of connection number surge during application scaling.

10、[Validating a new project](https://www.mostlypython.com/validating-a-new-project/)

The author open-sourced py-bugger, a tool that introduces specific types of bugs to assist in debugging education. He communicated face-to-face with other developers at PyCon's open spaces, discovered some new use cases and issues, emphasizing the importance of getting feedback through open spaces in the early stages of a project.

11、[Attention Wasn't All We Needed](https://www.stephendiehl.com/posts/post_transformers/)

Introduces a series of important technical improvements that have emerged in the Transformer model field since the famous "Attention Is All You Need" paper was published. The author uses the PyTorch framework and concise code examples to explain the core ideas of 14 important technologies and how they improve model inference speed and memory efficiency.

12、[Writing that changed how I think about PL](https://bernsteinbear.com/blog/pl-writing/)

The author shares more than 10 articles in the field of programming languages and compilers that have had a significant impact on their thinking, including garbage collector implementation, optimizer instruction rewriting, abstract domains and Z3 usage, correctness proofs of register allocation, regular expression engines, automatic differentiation, SSA form implementation, and more.

## [🐿️Projects & Resources](https://xiaobot.net/p/python_weekly)

1、[agenticSeek: Fully Local Manus AI](https://github.com/Fosowl/agenticSeek)

A 100% local alternative to Manus AI that supports voice, autonomous web browsing, code writing and task planning, with all data staying on local devices. (star 13.5K)

2、[django-allauth: Integrated set of Django applications addressing authentication](https://codeberg.org/allauth/django-allauth)

A Django application suite that provides complete user authentication, registration, account management, and third-party social account authentication functionality. Supports multiple authentication schemes (username or email login), multiple account verification strategies, and integrates OAuth 1.0/2.0, OpenID Connect, SAML 2.0 and other protocols.

3、[Ghost-Downloader-3: A cross-platform fluent-design AI-boost multi-threaded downloader](https://github.com/XiaoYouChR/Ghost-Downloader-3)

A cross-platform multi-threaded downloader developed based on Python, adopting Fluent Design style, with AI intelligent acceleration functionality, IDM-style intelligent chunked downloading, browser extension support and plugin system, supporting Windows, macOS and Linux platforms. (star 2.6K)

![Beautiful downloader](https://img.pythoncat.top/2025-05-30-downloader.png)

4、[vectorvfs: Your Filesystem as a Vector Database](https://github.com/perone/vectorvfs)

A lightweight Python package that converts Linux file systems into vector databases, storing vector embeddings directly outside files through VFS extended attributes, without requiring external indexes or database services.

5、[LivePortrait: Bring portraits to life!](https://github.com/KwaiVGI/LivePortrait)

Kuaishou's open-source portrait animation generation tool that supports efficient portrait animation creation, with stitching and redirection control functions, supporting portrait and animal modes, providing Gradio interface and one-click installation package. (star 15.5K)

![Bringing world famous paintings to life](https://img.pythoncat.top/2025-05-30_portrait.png)

6、[pgmpy: Python Library for Causal and Probabilistic Modeling using Bayesian Networks](https://github.com/pgmpy/pgmpy)

A professional Python causal and probabilistic modeling library based on Bayesian networks. Provides a complete set of probabilistic graphical model tools, suitable for machine learning and statistical analysis fields. (star 3K)

7、[MaiBot: Cyber Netizen for Group Chat](https://github.com/MaiM-with-u/MaiBot)

An interactive intelligent agent based on large models, focusing on group chat scenarios. Features intelligent conversation, real-time thinking, emotional expression, persistent memory and dynamic personality systems. (star 2.5K)

8、[magentic-ui: A research prototype of a human-centered web agent](https://github.com/microsoft/magentic-ui)

Microsoft's open-source human-computer collaborative web agent research prototype that can automate web tasks while maintaining user control, supporting collaborative planning, collaborative execution, action protection, plan learning and parallel task execution. (star 4.7K)

9、[vibe-draw: Turn your roughest sketches into stunning 3D worlds by vibe drawing](https://github.com/martin226/vibe-draw)

Converts rough hand-drawn sketches into beautiful 3D models. Supports free drawing, AI enhancement optimization, one-click 3D conversion, world building and model export functions. Developed based on Next.js, Three.js and FastAPI. (star 1.8K)

![Nice full-stack + AI project](https://img.pythoncat.top/2025-05-30-vibe-draw.jpeg)

10、[airweave: Airweave lets agents search any app](https://github.com/airweave-ai/airweave)

This intelligent agent can connect various applications, productivity tools and databases, converting their content into searchable knowledge bases and providing services to agents through standardized interfaces. (star 2.5K)

11、[flowshow: Just a super thin wrapper for Python tasks that form a flow](https://github.com/koaning/flowshow)

It provides @task decorators to track and visualize function execution flows. Supports retry mechanisms, logging, context managers and interactive visualization interfaces.

12、[ai-baby-monitor: Local Video-LLM powered AI Baby Monitor](https://github.com/zeenolife/ai-baby-monitor)

An intelligent baby monitoring system based on local video large models that monitors in real-time through cameras, performs real-time analysis according to safety rules, and issues gentle reminder sounds when violations of safety rules are detected.

## [🐢Podcasts & Videos](https://xiaobot.net/p/python_weekly)

1、[PyCon US 2025 Video List](https://www.youtube.com/playlist?list=PL2Uw4_HvXqvb98mQjN0-rYQjdDxJ_hcrs)

This year's PyCon US videos were released very early! See if there are any topics that interest you?

2、[PyTexas 2025 Video List](https://www.youtube.com/playlist?list=PL0MRiRrXAvRiSmPn_LDdhDbtZwu6g4xct)

The PyTexas event in Texas, USA has released 21 presentation videos.

## [🥂Discussions & Questions](https://xiaobot.net/p/python_weekly)

1、[Add Virtual Threads to Python](https://discuss.python.org/t/add-virtual-threads-to-python/91403)

Python core developer Mark Shannon (yes, the proposer of Faster CPython, who was recently laid off by Microsoft) proposed the idea of adding virtual threads to Python, believing that virtual threads can handle concurrency better than async/await. The post introduces the advantages and implementation methods of this approach, sparking widespread discussion in the community.

2、[What CPython Layoffs Taught Me About the Real Value of Expertise](https://www.reddit.com/r/Python/comments/1kok2e1/what_cpython_layoffs_taught_me_about_the_real/)

Microsoft's layoffs of the CPython and TypeScript compiler teams triggered the author's deep thinking about the value of technical expertise. Should we focus on output rather than architecture, on impact rather than elegance? How to balance technical depth with business value?

## [🐧 Past Reviews](https://xiaobot.net/p/python_weekly)

[Python Weekly #54: ChatTTS Powerful Text-to-Speech Model](https://pythoncat.top/posts/2024-06-08-weekly) (2024.06.08)

[Python Weekly #4: Python 2023 Language Summit](https://pythoncat.top/posts/2023-05-31-weekly4) (2023.05.31)

