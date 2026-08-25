#import "../skills/cv-tuning/resources/harvard_cv.typ": cv, cv_section, cv_experience, cv_entry

#show: cv.with(
  name: "LUONG DO MINH HUNG",
  title: "Expert, Software Engineering (Architecture, Reliability & Multi-Platform)",
  contact: "minhhung2556@gmail.com · (+84) 775005110 · Ho Chi Minh City, Vietnam",
)

#cv_section("Professional Summary")
Expert Software Engineer and Technical Lead with 13+ years of experience (10+ years leading engineering teams and system architecture) delivering mission-critical financial, payment, and e-commerce platforms (Home Credit, Sendo, SenPay). Deep technical expertise spanning Mobile (Dart/Flutter, Swift, Kotlin, Android, iOS), Backend (Java, Python, OpenAPI/REST), and Web (TypeScript, ReactJS). Proven track record in low-level architecture design, SOLID principles, design patterns, and runtime/compilation optimization. Highly accomplished in mentoring Officer-level and senior engineers, driving peer code reviews, establishing test automation (unit, integration, contract testing), collaborating with QE on defect triage, and hardening enterprise security (OWASP, FIDO, TLS, App Attest).

#cv_section("Core Competencies")
- *Architecture & Low-Level Design:* Low-Level Architecture, SOLID Principles, Design Patterns, Microservices & Modular Platforms, High Concurrency & Scalability, Compiling & Runtime Deep Understanding.
- *Code Quality, Testing & Reliability:* Peer Code Reviews, Coding Standards Enforcement, Unit / Integration / Contract Testing, Test Automation, Defect Triage & QE Collaboration, Observability (Logging, Monitoring, Tracing).
- *Technical Leadership & Mentorship:* Mentoring Officer & Senior Engineers, Engineering Best Practices, Process Improvement, Cross-Functional Team Leadership, Technical Documentation (System Design, API Specs, Guidelines).
- *Multi-Platform Engineering:* Mobile (Dart/Flutter, Swift, Kotlin, Android, iOS Native), Backend (Java, Spring Boot, Python/FastAPI, RESTful APIs), Web (TypeScript, ReactJS, Next.js), Azure CI/CD Pipelines.
- *Enterprise Security & Hardening:* OWASP Mobile Top 10, MASVS, Secure Auth & FIDO Passkeys, TLS & Certificate Pinning, Threat Modeling, Google Play Integrity & Apple App Attest, Vulnerability Scanning (OSV/SCA), RASP.

#cv_section("Experience")

#cv_experience(
  company: "EmbedIT Vietnam",
  location: "Ho Chi Minh City",
  role: "Mobile Technical Lead / Senior Software Engineer",
  dates: "April 2022 – Present",
  bullets: (
    [Lead low-level architecture design and software component engineering for Home Credit digital payment and transaction systems across Vietnam and the Philippines, ensuring efficiency, scalability, and security.],
    [Serve on Technical Governance Committee: establish coding guidelines, enforce SOLID principles and design patterns, lead peer code reviews, and mentor Officer-level and senior engineers across distributed teams.],
    [Champion test automation and reliability: define unit, integration, and contract testing protocols; collaborate with QE teams to diagnose, troubleshoot, and remediate complex production defects.],
    [Author and maintain structured technical documentation, including OpenAPI specifications, low-level system design documents, and architectural guidelines for multi-country platforms.],
    [Automated vulnerability scanning and security reporting by integrating Google Open Source Vulnerability Scanner into Azure CI/CD pipelines, ensuring threat-resilient production deployments.],
    [Built internal developer tooling and Dart CLI generators from UML/OpenAPI specs, improving compile-time safety and accelerating delivery workflows.],
  )
)

#cv_experience(
  company: "Home Credit Vietnam",
  location: "Ho Chi Minh City",
  role: "Mobile Technical Lead",
  dates: "December 2020 – April 2022",
  bullets: (
    [Architected and delivered core high-volume digital payment streams (mobile top-up, utility bills, QR payments, PayLater) scaling across 4 markets (Vietnam, Philippines, Indonesia, India).],
    [Audited legacy codebase and runtime performance; diagnosed security root causes, eliminated insecure third-party SDKs saving >€10,000/year, and optimized application size by 20–50%.],
    [Designed country-specific modular architecture and unified native Android/iOS-to-Flutter integration layer across 5 cross-functional engineering teams.],
    [Mentored developers on best practices and clean architecture; authored mobile development guidelines and delivered technical training sessions; recognized with the DNA Star leadership award.],
  )
)

#cv_experience(
  company: "Sendo.vn",
  location: "Ho Chi Minh City",
  role: "Mobile Team Leader (Technical)",
  dates: "May 2018 – December 2020",
  bullets: (
    [Directed mobile engineering for top-4 Vietnam e-commerce platform; pioneered Vietnam's first Flutter super-app covering payment gateways (SenPay, ZaloPay, bank cards), flash sales, and high-traffic event systems.],
    [Resolved low-level rendering, multithreading, and concurrency bottlenecks hands-on, optimizing system responsiveness and runtime stability.],
    [Scaled engineering organization to 10+ cross-functional teams (100+ engineers); established rigorous code review standards, test automation workflows, and technical coaching programs.],
  )
)

#cv_experience(
  company: "SenPay.vn",
  location: "Ho Chi Minh City",
  role: "Android Team Leader",
  dates: "May 2017 – May 2018",
  bullets: (
    [Architected and built SenPay e-wallet and payment gateway Android application from scratch; published on Google Play with end-to-end security hardening and transaction reliability.],
    [Delivered digital payment features: phone top-ups, utility bill payments, e-wallet management, and domestic/international card processing; earned rapid promotions from Android Developer to Team Lead.],
  )
)

#cv_experience(
  company: "FinViet",
  location: "Ho Chi Minh City",
  role: "Senior Mobile App Developer",
  dates: "April 2017 – May 2017",
  bullets: (
    [Architected and prototyped FinViet Eco financial services application in React Native during early framework adoption, designing resilient client-server data synchronization.],
  )
)

#cv_experience(
  company: "Mobivi – iCareBenefits",
  location: "Ho Chi Minh City",
  role: "Android Team Leader",
  dates: "June 2015 – June 2016",
  bullets: (
    [Architected and shipped 6+ logistics and enterprise transaction apps from scratch (e-commerce, field sales, delivery tracking, customer service) with offline sync and reliable data workflows.],
  )
)

#cv_experience(
  company: "ME Corp",
  location: "Ho Chi Minh City",
  role: "Mobile App Developer",
  dates: "June 2012 – June 2015",
  bullets: (
    [Developed high-concurrency online gaming platform (20+ games, chat, event payment microservices) servicing 30M users using Java/J2ME and LibGDX; earned Best Employee recognition (2014).],
  )
)

#cv_section("Technical Skills")
- *Programming Languages:* Dart, Kotlin, Swift, Java, TypeScript, JavaScript, Python.
- *Architecture & Design:* Low-Level System Design, SOLID Principles, Design Patterns, Microservices, Modular Super-App Architecture, High Concurrency & Low Latency, Compiling & Runtime Deep Understanding, UML.
- *Code Quality & Testing:* Unit Testing, Integration Testing, Contract Testing, Test Automation, Peer Code Reviews, QE Collaboration, Observability (Logging, Monitoring, Tracing), Technical Documentation (API Specs, System Design).
- *Platforms & Frameworks:* Flutter, Android (Native), iOS (Native), ReactJS, Next.js, FastAPI, Spring Boot, RESTful APIs, OpenAPI.
- *Security & Infrastructure:* OWASP Mobile Top 10, MASVS, FIDO Passkeys, TLS & Certificate Pinning, Google Play Integrity, Apple App Attest, Vulnerability Scanning (OSV/SCA), Threat Modeling, Azure Pipelines, CI/CD.
- *Domains:* Banking & Fintech, Digital Payments (QR, E-Wallets, Bill Pay, PayLater), E-Commerce Super-Apps, Real-Time High-Volume Systems.

#cv_section("Selected Credentials and Speaking")
#cv_entry(
  title: "Executive Leadership Certification",
  subtitle: "High-Impact IT Leader (CIO / CTO / IT Director)",
  dates: "2023",
)
#cv_entry(
  title: "Speaker & Mentor",
  subtitle: "Home Credit TechTalks (2021) · Google DevFest HCM Flutter Training (2021)",
  dates: "2021",
)
#cv_entry(
  title: "Technical Author",
  subtitle: "Home Credit IT Blog Series · Medium (romanticdeveloper.medium.com)",
  dates: "2021 – Present",
)

#cv_section("Reference Links")
- *Home Credit Application:* https://www.homecredit.vn/ung-dung-home-credit
- *Sendo & SenPay Platform:* https://www.sendo.vn · https://senpay.vn
- *Personal Website & GitHub:* https://romanticdeveloper.com · https://github.com/minhhung2556

#cv_section("Education")
#cv_entry(
  title: "Tra Vinh University",
  subtitle: "Bachelor of Information Technology (GPA 3.7/4.0 · Completed, graduation pending)",
  dates: "2024 – 2026",
)
#cv_entry(
  title: "Open University Ho Chi Minh City",
  subtitle: "Associate's Degree, Computer Science (Perfect score on Computer Graphics)",
  dates: "2008 – 2011",
)
