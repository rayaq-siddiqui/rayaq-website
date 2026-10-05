CONTACT = {
    "email": "rayaq05@hotmail.com",
    "linkedin": "https://linkedin.com/in/rayaq-siddiqui",
    "github": "https://github.com/rayaq-siddiqui",
}

HEADLINE = "Software Engineer @ Google · University of Waterloo SE Alum"
LOCATION = "San Francisco, CA"

SUMMARY = (
    "I enjoy working on complex problems across software engineering and mathematics. "
    "These days that means software engineering, machine learning, and compilers, and I'm happiest "
    "when one problem drags in all three."
)

EDUCATION = {
    "school": "University of Waterloo",
    "location": "Waterloo, ON",
    "degree": "Bachelor of Engineering in Software Engineering, Specialization in AI",
    "dates": "Apr. 2025",
    "details": "Graduated with Distinction. Coursework in Algorithms, Data Structures, Operating Systems, "
    "Concurrency, Compilers, Databases, Adv. C++, Computer Vision. Member of the UW Data Science Club "
    "and WATonomous.",
    "badge": {"initials": "UW", "bg": "#FFD100", "fg": "#000000"},
}

EXPERIENCES = [
    {
        "company": "Google",
        "url": "https://about.google/",
        "location": "Sunnyvale, CA",
        "role": "Software Engineer",
        "stack": "C++, Rust, TypeScript, VCS, Concurrency, Microservices, Software Design & Architecture",
        "dates": "Jul. 2025 – Present",
        "bullets": [
            'Building <a href="https://github.com/jj-vcs/jj" target="_blank" rel="noopener"><strong>JJ</strong></a>, '
            "on track to become the <strong>primary VCS for every engineer at Google</strong>; contributing to its "
            "open-source project and internal Rust CLI",
            "Scaling JJ's distributed C++ and Rust APIs to absorb Google-wide load from engineers and coding agents "
            "alike, via concurrency, load balancing, caching, and rate limiting",
            "Built <strong>agent-driven development workflows</strong> – automated code review agents, scheduled "
            "agent jobs, and prompt-engineered orchestration pipelines – to accelerate the software development "
            "life cycle",
            "Maintaining <strong>high test coverage</strong> across JJ's Rust CLI and internal contributions, "
            "prioritized by module criticality",
            "Authoring design docs and technical plans for new JJ features across Google's internal developer tooling",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/google", "bg": "#ffffff"},
    },
    {
        "company": "Google",
        "url": "https://about.google/",
        "location": "Toronto, ON",
        "role": "Software Engineer Intern",
        "stack": "Go, GCP, Concurrency, Distributed Computing, Databases, API, Microservices",
        "dates": "May 2024 – Aug. 2024",
        "bullets": [
            "Built on <strong>Remote Build Execution</strong>, accelerating remote builds for clients including "
            "Chrome, Android & TensorFlow",
            "Operated across globally distributed GCP infrastructure and sharded Spanner databases under a "
            "microservice architecture",
            "Developed an instance-monitoring system that kept live migrations consistent with expected system state",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/google", "bg": "#ffffff"},
    },
    {
        "company": "d-Matrix",
        "url": "https://www.d-matrix.ai/",
        "location": "Toronto, ON",
        "role": "Machine Learning Compiler Engineer Intern",
        "stack": "C++, PyTorch, LLVM, MLIR, torch-MLIR",
        "dates": "Jan. 2024 – Apr. 2024",
        "bullets": [
            "<strong>Accelerated generative AI (LLM, diffusion) inference by 20x</strong> via systems-level "
            "architecture work in C++ on the ML compiler stack",
            "Implemented 2D convolution, pooling, ResNet, Stable Diffusion, LLaVA & Vision Transformer support in "
            "the frontend compiler – the first working convolution ops on the platform",
            "Built LLaMA 2 operations and transformations on top of the LLVM MLIR and torch-MLIR project architecture",
            "Led integration of the LLaMA 3 decoder and full model, achieving a <strong>17.5x runtime speedup</strong>",
        ],
        "icon": {"type": "initials", "initials": "dM", "bg": "#7C3AED", "fg": "#ffffff"},
    },
    {
        "company": "IBM",
        "url": "https://www.ibm.com",
        "location": "Toronto, ON",
        "role": "Machine Learning Engineer Intern",
        "stack": "Python, C++, PyTorch, Computer Vision, CUDA, AWS SageMaker",
        "dates": "May 2023 – Aug. 2023",
        "bullets": [
            "Built scalable ML software to automate object-detection tasks in Python and PyTorch",
            "Pruned & quantized Facebook Research's Faster R-CNN for a facial-analysis model serving "
            "<strong>9M users/year</strong>, cutting manual verification hours <strong>75%</strong> and saving "
            "<strong>$35M</strong> annually",
            "Trained on CUDA GPUs to <strong>99% accuracy</strong> and a <strong>0.99 F1-score</strong>, while "
            "shrinking model size by <strong>78%</strong>",
        ],
        "icon": {"type": "initials", "initials": "IBM", "bg": "#052FAD", "fg": "#ffffff"},
    },
    {
        "company": "BlackBerry Limited",
        "url": "https://www.blackberry.com",
        "location": "Waterloo, ON",
        "role": "Machine Learning Engineer Intern",
        "stack": "Python, TensorFlow, NLP, Elasticsearch, Docker, AWS S3, SageMaker, EC2",
        "dates": "Sept. 2022 – Dec. 2022",
        "bullets": [
            "Built a log anomaly detection platform combining NLP, data pipelines, and Elasticsearch in Python",
            "Raised NLP model accuracy from <strong>60% to 91%</strong> and F1-score from <strong>0.30 to 0.87</strong>",
            "Productionized two anomaly detection models (Autoencoder + Isolation Forest; Transformer per "
            '<a href="https://arxiv.org/abs/1706.03762" target="_blank" rel="noopener">Google\'s paper</a>) '
            "with a retraining pipeline on TensorFlow, Docker, AWS S3, SageMaker & EC2, shipped through GitLab CI/CD",
            "Made inference <strong>~382x faster</strong> and cut low-level memory use <strong>52%</strong> through "
            "memory tracing, profiling, and multiprocessing",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/blackberry/ffffff", "bg": "#000000"},
    },
    {
        "company": "RBC",
        "url": "https://www.rbc.com/about-rbc.html",
        "location": "Toronto, ON",
        "role": "Software Engineer Intern",
        "stack": "Python, Django, SQL, Exchangelib",
        "dates": "Jan. 2022 – Apr. 2022",
        "bullets": [
            "Built a Python/Django dashboard integrating <strong>7 data sources</strong> into a single operational view",
            "Built an automated mailing-response system that saved an estimated <strong>600 hours/month</strong>",
            "Integrated a cloud database using Exchangelib, automated scripts, Django models & SQL queries",
        ],
        "icon": {"type": "initials", "initials": "RBC", "bg": "#005DAA", "fg": "#ffffff"},
    },
    {
        "company": "Polar (now Nova)",
        "location": "Toronto, ON",
        "role": "Software Engineer Intern",
        "stack": "Python, JavaScript/TypeScript, React, jQuery, Node.js, Selenium",
        "dates": "May 2021 – Aug. 2021",
        "bullets": [
            "Contributed on the Creative Pod, developing an interactive iframe with Python, JavaScript/TypeScript, "
            "React, jQuery, Node.js, and Selenium — building features, fixing bugs, and writing unit tests in a "
            "test-driven, agile environment",
            "Transitioned the codebase from Sinon/Chai to Jest using the Jest-Extended library, resulting in 2x "
            "faster tests running independently in parallel across threads",
            "Replaced library implementations with hand-written algorithms across two repositories, speeding up "
            "selected components by 2–8x",
        ],
        "icon": {"type": "initials", "initials": "P", "bg": "#0EA5E9", "fg": "#ffffff"},
    },
]

PROJECTS = [
    {
        "name": "CloudMesh, Decentralized ML Platform (FYDP)",
        "stack": "Python, C++, Distributed ML, Networking",
        "bullets": [
            "Leading extensive research into "
            '<a href="https://github.com/DCP-CloudMesh/DistributedML" target="_blank" rel="noopener">'
            "advanced distributed ML algorithms</a> (data parallelism, federated learning)",
            "Implementing a "
            '<a href="https://github.com/DCP-CloudMesh/PeerToPeer" target="_blank" rel="noopener">'
            "P2P architecture</a> to enable the connection of devices across large-scale distributed networks",
        ],
    },
    {
        "name": "Text Recognition Glasses",
        "stack": "Python, Computer Vision, OCR, NLP",
        "bullets": [
            "A wearable that reads text in front of the user, combining optical character recognition with "
            "natural-language processing",
        ],
    },
    {
        "name": "PharmaHacks Multi-Disease Classification",
        "stack": "Python, Deep Learning, Classification",
        "bullets": [
            "<strong>Winner</strong> at the Pfizer/McGill-sponsored PharmaHacks hackathon, classifying multiple "
            "diseases from gastrointestinal data",
        ],
    },
    {
        "name": "UltraAnalysis",
        "stack": "Python, Computer Vision, UNet, ENet",
        "bullets": [
            "Semantic segmentation and classification of ultrasound images with UNet and ENet to identify "
            "malignant cell clusters",
        ],
    },
    {
        "name": "Semantic Segmentation for Self-Driving Cars",
        "stack": "Python, Deep Learning, Computer Vision",
        "bullets": [
            "Semantic segmentation of autonomous-driving imagery, classifying every pixel of each frame",
        ],
    },
]

LEADERSHIP = [
    {
        "name": "Kids Caring for Kids Cancer Drive",
        "role": "Lead · Jul. 2018 – Jun. 2020",
        "bullets": [
            "Led a campaign that raised <strong>over $80,000</strong> across two years for pediatric cancer care "
            "and research in Northern Ontario",
        ],
    },
    {
        "name": "Lockerby Students' Council",
        "role": "Vice President & Treasurer · Sep. 2017 – Jun. 2020",
        "bullets": [
            "Held student-government leadership across three academic years, and organized a mental-health "
            "conference for 200+ students transitioning into high school",
        ],
    },
]

HONORS = [
    "Governor General's Academic Medal",
    "Valedictorian",
    "Most Outstanding Student Award",
    "Ontario Principals' Council Award",
    "15 Subject Awards (Highest Mark in Grade)",
    "Cayley & Fermat Math Contest School Champion",
    "Ontario Scholar",
    "AP Scholar",
]

CERTIFICATIONS = [
    "Microsoft Certified: Azure AI Engineer Associate (2026)",
    "Google Cloud Generative AI Leader (2026)",
    "Deep Learning Specialization (2024)",
    "IBM DevOps and Software Engineering Professional Certificate (2024)",
    "IBM AI Enterprise Workflow V1 (2023)",
    "IBM AI Engineering Professional Certificate (2023)",
    "Machine Learning Specialization (2022)",
]

SKILLS = {
    "Languages": ["Python", "C++", "Rust", "Go", "C", "JavaScript/TypeScript", "SQL", "Bash", "Java", "CUDA"],
    "ML & Compilers": [
        "PyTorch",
        "TensorFlow",
        "LLVM",
        "MLIR",
        "torch-MLIR",
        "HuggingFace",
        "LangChain",
        "NumPy",
        "Pandas",
    ],
    "Infrastructure & Tools": [
        "GCP",
        "AWS",
        "Docker",
        "Bazel",
        "Spanner",
        "Elasticsearch",
        "Django",
        "FastAPI",
        "Spark",
        "Git",
    ],
}
