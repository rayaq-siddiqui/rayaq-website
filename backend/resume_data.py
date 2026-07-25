CONTACT = {
    "email": "rayaq05@hotmail.com",
    "linkedin": "https://linkedin.com/in/rayaq-siddiqui",
    "github": "https://github.com/rayaq-siddiqui",
}

HEADLINE = "Software Engineer @ Google · University of Waterloo SE Alum"
LOCATION = "San Francisco, CA"

SUMMARY = (
    "I enjoy working on complex problems across software engineering, machine learning, "
    "and mathematics. My experience spans compilers and low-level systems, machine "
    "learning training, optimization and deployment, and large-scale build and version "
    "control infrastructure."
)

EDUCATION = {
    "school": "University of Waterloo",
    "location": "Waterloo, ON",
    "degree": "Bachelor of Engineering in Software Engineering, Specialization in AI",
    "dates": "Apr. 2025",
    "details": "Algorithms, Data Structures, Operating Systems, Concurrency, Compilers, "
    "Databases, Adv. C++, Computer Vision",
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
            'Working on <a href="https://github.com/jj-vcs/jj" target="_blank" rel="noopener">JJ</a> – a modern '
            "version control system to accelerate developer productivity for Google worldwide",
            "Scaling distributed systems and enhancing APIs for JJ's version control operations in C++. Using concurrent operations, load balancers, various caching mechanisms, and rate limiting to deal with scale of requests",
            "Contributing to JJ's open source project and internal CLI in Rust. Writing comprehensive tests to ensure reliability",
            "Developing design documents and plans for new features to interact with various Google internal tooling",
            "Utilizing agent orchestration and prompt engineering to streamline development life cycle",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/google", "bg": "#ffffff"},
    },
    {
        "company": "Google",
        "url": "https://about.google/",
        "location": "Toronto, ON",
        "role": "Software Engineer",
        "stack": "Go, GCP, Concurrency, Distributed Computing, Databases, API, Microservices",
        "dates": "May 2024 – Aug. 2024",
        "bullets": [
            "Working on Remote Build Execution – accelerating remote builds for clients like Chrome, Android & TensorFlow",
            "Utilizing globally distributed Google Cloud Platform (GCP) projects, secure internal cloud infrastructure, sharded Spanner databases, and working with multiple internal API services, following a microservice architecture",
            "Developing an instance monitoring system that ensures instances' migrations match the system's state",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/google", "bg": "#ffffff"},
    },
    {
        "company": "d-Matrix",
        "url": "https://www.d-matrix.ai/",
        "location": "Toronto, ON",
        "role": "Machine Learning Compiler Engineer",
        "stack": "C++, PyTorch, LLVM, MLIR, Convolution",
        "dates": "Jan. 2024 – Apr. 2024",
        "bullets": [
            "Accelerated Generative AI (LLM, SD) model inferencing by 20x focusing on compiler-level architecture in C++",
            "Implemented 2D Convolution, Average & Max Pooling, ResNet models, Stable Diffusion, LLaVa and Vision Transformers in the front-end compiler. First ever proof of life of convolution-like operations on our compiler",
            "Developed operations & transformations for LLaMa2 on top of LLVM MLIR & torch-MLIR project architecture",
            "Spearheaded integration of LLaMa3 Decoder and Full Model into our compiler achieving 17.5x speedup in runtime",
        ],
        "icon": {"type": "initials", "initials": "dM", "bg": "#7C3AED", "fg": "#ffffff"},
    },
    {
        "company": "IBM",
        "url": "https://www.ibm.com",
        "location": "Toronto, ON",
        "role": "Machine Learning Engineer",
        "stack": "Python, C++, PyTorch, CV, AWS SageMaker",
        "dates": "May 2023 – Aug. 2023",
        "bullets": [
            "Developed scalable ML software architecture to automate object detection tasks using Python and PyTorch",
            "Implemented, pruned, & quantized Facebook Research's Faster R-CNN model for a facial analysis task, used by 9 million users/year, reduced manual verification hours by 75%, and saved $35 million USD costs annually",
            "Trained model on a CUDA GPU and produced accuracy of 99%, F1-score of 0.99, and model size reduced by 78%",
        ],
        "icon": {"type": "initials", "initials": "IBM", "bg": "#052FAD", "fg": "#ffffff"},
    },
    {
        "company": "BlackBerry Limited",
        "url": "https://www.blackberry.com",
        "location": "Waterloo, ON",
        "role": "Machine Learning Engineer",
        "stack": "Python, TensorFlow, NLP, NoSQL, Docker, AWS S3, EC2",
        "dates": "Sept. 2022 – Dec. 2022",
        "bullets": [
            "Developed a log anomaly detection platform combining NLP, data pipelines, and Elasticsearch using Python",
            "Implemented NLP model and improved model accuracy from 60% to 91% and F1-score from 0.30 to 0.87",
            "Productionized two anomaly detection models (Autoencoder + Isolation Forest AND Transformer "
            'architecture based on <a href="https://arxiv.org/abs/1706.03762" target="_blank" rel="noopener">'
            "Google's paper</a>) and retraining pipeline using TensorFlow, Docker, AWS S3, SageMaker & EC2",
        ],
        "icon": {"type": "img", "src": "https://cdn.simpleicons.org/blackberry/ffffff", "bg": "#000000"},
    },
    {
        "company": "RBC",
        "url": "https://www.rbc.com/about-rbc.html",
        "location": "Toronto, ON",
        "role": "Software Engineer",
        "stack": "Python, Django, SQL, Exchangelib",
        "dates": "Jan. 2022 – Apr. 2022",
        "bullets": [
            "Spearheaded a comprehensive dashboard with 7 data source system integrations using Python and Django",
            "Improved productivity by saving 600 hours/month by developing an automated mailing response system",
            "Integrated a cloud database using Exchangelib, automated scripts, Django models & SQL queries",
        ],
        "icon": {"type": "initials", "initials": "RBC", "bg": "#005DAA", "fg": "#ffffff"},
    },
    {
        "company": "Polar",
        "location": "Toronto, ON",
        "role": "Software Engineer",
        "stack": "Python, JavaScript/TypeScript, React, jQuery, Node.js, Selenium",
        "dates": "May 2021 – Aug. 2021",
        "bullets": [
            "Contributed on the Creative Pod, developing an interactive iframe with Python, JavaScript/TypeScript, "
            "React, jQuery, Node.js, and Selenium — building features, fixing bugs, and writing unit tests in a "
            "test-driven, agile environment",
            "Transitioned the codebase from Sinon/Chai to Jest using the Jest-Extended library, resulting in 2x "
            "faster tests running independently in parallel across threads",
            "Optimized two repositories by replacing libraries with manually implemented algorithms, increasing "
            "runtime of numerous components by 2–8x",
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
]

HONORS = [
    "Governor General's Academic Medal",
    "Valedictorian",
    "Most Outstanding Student Award",
    "Ontario Principals' Council Award",
    "15 Subject Awards (Highest Mark in Grade)",
]

CERTIFICATIONS = [
    "Deep Neural Networks with PyTorch",
    "Building Deep Learning Models with TensorFlow",
    "Introduction to Deep Learning & Neural Networks with Keras",
    "Introduction to Computer Vision and Image Processing",
    "Machine Learning With Python",
]

SKILLS = {
    "Languages": ["Python", "C++", "Rust", "Go", "C", "JavaScript", "SQL", "Bash", "Java", "CUDA"],
    "Frameworks": [
        "PyTorch",
        "TensorFlow",
        "AWS",
        "Docker",
        "NumPy",
        "Pandas",
        "Django",
        "Spark",
        "LangChain",
        "HuggingFace",
        "Bazel",
        "FastAPI",
    ],
}
