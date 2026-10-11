const API_BASE =
    "http://127.0.0.1:8000";


let currentResumeId = null;
let currentJobId = null;

let currentInterviewSessionId = null;
let currentQuestionId = null;
let currentQuestionNumber = 1;

let resumeItems = [];
let jobItems = [];



/* =====================================================
   API
===================================================== */

async function apiFetch(
    path,
    options = {}
) {

    const headers = {
        ...(options.headers || {})
    };

    /*
     * CareerAI custom authentication token.
     *
     * Resume Analysis and other protected
     * backend endpoints require this token.
     */
    const authToken =
        localStorage.getItem(
            "careerai_token"
        );

    if (authToken) {

        headers["Authorization"] =
            `Bearer ${authToken}`;
    }

    /*
     * Only send JSON Content-Type when the
     * request body is NOT FormData.
     *
     * This is important for PDF uploads.
     */
    if (
        options.body &&
        !(options.body instanceof FormData)
    ) {

        headers["Content-Type"] =
            "application/json";
    }

    const response =
        await fetch(
            API_BASE + path,
            {
                ...options,
                headers: headers
            }
        );

    let data = null;

    try {

        data =
            await response.json();

    }

    catch (_) {

        data = null;

    }

    if (!response.ok) {

        throw new Error(
            data?.detail ||
            data?.message ||
            `Request failed (${response.status})`
        );

    }

    return data;
}


/* =====================================================
   PAGE NAVIGATION
===================================================== */

function showPage(
    pageName
) {

    document
        .querySelectorAll(".page")
        .forEach(
            function (page) {

                page.classList.remove(
                    "active-page"
                );

            }
        );


    const target =
        document.getElementById(
            pageName
        );


    if (target) {

        target.classList.add(
            "active-page"
        );

    }


    document
        .querySelectorAll(".nav-item")
        .forEach(
            function (item) {

                item.classList.toggle(
                    "active",
                    item.dataset.page ===
                    pageName
                );

            }
        );


    const titles = {

        dashboard:
            "Career Dashboard",

        resume:
            "Resume Intelligence",

        "saved-resumes":
            "My Resumes",

        job:
            "Job Intelligence",

        matching:
            "Career Matching",

        interview:
            "AI Interview"

    };


    const title =
        document.getElementById(
            "pageTitle"
        );


    if (title) {

        title.textContent =
            titles[pageName] ||
            "Career Dashboard";

    }


    if (
        pageName ===
        "saved-resumes"
    ) {

        loadSavedResumes();

    }


    if (
        pageName ===
        "matching"
    ) {

        loadSavedResumes()
            .then(
                loadSavedJobs
            );

    }


    if (
        pageName ===
        "interview"
    ) {

        loadSavedResumes()
            .then(
                loadSavedJobs
            );

    }


    window.scrollTo({
        top:0,
        behavior:"smooth"
    });

}



/* =====================================================
   SIDEBAR
===================================================== */

function toggleSidebar() {

    const collapsed =
        document.body.classList.toggle(
            "sidebar-collapsed"
        );


    localStorage.setItem(
        "careerai_sidebar_collapsed",
        collapsed
            ? "true"
            : "false"
    );


    const button =
        document.getElementById(
            "sidebarToggle"
        );


    if (button) {

        button.title =
            collapsed
                ? "Expand sidebar"
                : "Collapse sidebar";

    }

}



function restoreSidebarState() {

    if (
        localStorage.getItem(
            "careerai_sidebar_collapsed"
        ) === "true"
    ) {

        document.body.classList.add(
            "sidebar-collapsed"
        );


        const button =
            document.getElementById(
                "sidebarToggle"
            );


        if (button) {

            button.title =
                "Expand sidebar";

        }

    }

}



/* =====================================================
   LOGOUT
===================================================== */

async function logoutFromClerk() {

    try {

        if (
            typeof Clerk !==
                "undefined" &&
            Clerk.signOut
        ) {

            await Clerk.signOut();

        }

        else {

            window.location.reload();

        }

    }

    catch (error) {

        console.error(
            "Clerk logout failed:",
            error
        );


        alert(
            "Logout failed. Please try again."
        );

    }

}



/* =====================================================
   CLEAR
===================================================== */

function clearWorkspace() {

    currentResumeId = null;
    currentJobId = null;

    currentInterviewSessionId =
        null;

    currentQuestionId =
        null;

    currentQuestionNumber =
        1;


    [
        "resumeFile",
        "jobFile"
    ].forEach(
        function (id) {

            const element =
                document.getElementById(
                    id
                );


            if (element) {

                element.value =
                    "";

            }

        }
    );


    setText(
        "resumeFileName",
        "No file selected"
    );


    setText(
        "jobFileName",
        "No file selected"
    );


    setText(
        "evaluationContent",
        ""
    );


    setText(
        "reportContent",
        ""
    );


    const match =
        document.getElementById(
            "matchResult"
        );


    const interview =
        document.getElementById(
            "interviewPanel"
        );


    const evaluation =
        document.getElementById(
            "evaluationPanel"
        );


    const finalReport =
        document.getElementById(
            "finalReport"
        );


    if (match) {

        match.classList.add(
            "hidden"
        );

    }


    if (interview) {

        interview.classList.add(
            "hidden"
        );

    }


    if (evaluation) {

        evaluation.classList.add(
            "hidden"
        );

    }


    if (finalReport) {

        finalReport.classList.add(
            "hidden"
        );

    }


    showToast(
        "Workspace cleared."
    );

}



/* =====================================================
   TOAST
===================================================== */

function showToast(
    message
) {

    const toast =
        document.getElementById(
            "toast"
        );


    if (!toast) {

        return;

    }


    toast.textContent =
        message;


    toast.classList.add(
        "show"
    );


    clearTimeout(
        window.__careerToastTimer
    );


    window.__careerToastTimer =
        setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            2800
        );

}



/* =====================================================
   HELPERS
===================================================== */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.textContent =
            value ?? "";

    }

}



function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}



function prettyKey(
    key
) {

    return String(key)

        .replaceAll(
            "_",
            " "
        )

        .replace(
            /\b\w/g,
            function (character) {

                return character.toUpperCase();

            }
        );

}



/* =====================================================
   GENERIC AI RESULT RENDERER
===================================================== */

function renderValue(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return `
            <span class="muted-result">
                Not available
            </span>
        `;

    }


    if (
        Array.isArray(value)
    ) {

        if (
            value.length === 0
        ) {

            return `
                <span class="muted-result">
                    None identified
                </span>
            `;

        }


        return `
            <ul class="ai-list">

                ${
                    value
                        .map(
                            function (item) {

                                return `
                                    <li>
                                        ${
                                            typeof item ===
                                            "object"
                                                ? renderValue(item)
                                                : escapeHtml(item)
                                        }
                                    </li>
                                `;

                            }
                        )
                        .join("")
                }

            </ul>
        `;

    }


    if (
        typeof value ===
        "object"
    ) {

        return `

            <div class="ai-object">

                ${
                    Object
                        .entries(value)
                        .map(
                            function (
                                [key, item]
                            ) {

                                return `

                                    <div class="ai-field">

                                        <strong>
                                            ${escapeHtml(
                                                prettyKey(key)
                                            )}
                                        </strong>

                                        ${renderValue(
                                            item
                                        )}

                                    </div>

                                `;

                            }
                        )
                        .join("")
                }

            </div>

        `;

    }


    return `
        <p>
            ${escapeHtml(value)}
        </p>
    `;

}



function renderAnalysis(
    containerId,
    data
) {

    const container =
        document.getElementById(
            containerId
        );


    if (!container) {

        return;

    }


    let analysis =
        data?.analysis ||
        data?.analysis_json ||
        data;


    if (!analysis) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ✦
                </div>

                <h3>
                    No analysis returned
                </h3>

            </div>

        `;

        return;

    }


    if (
        typeof analysis ===
        "string"
    ) {

        try {

            analysis =
                JSON.parse(
                    analysis
                );

        }

        catch (_) {

            container.innerHTML =
                `<p>${escapeHtml(
                    analysis
                )}</p>`;

            return;

        }

    }


    if (
        typeof analysis !==
        "object"
    ) {

        container.innerHTML =
            `<p>${escapeHtml(
                analysis
            )}</p>`;

        return;

    }


    container.innerHTML = `

        <div class="ai-result">

            ${
                Object
                    .entries(analysis)
                    .map(
                        function (
                            [key, value]
                        ) {

                            return `

                                <div
                                    class="ai-result-card"
                                >

                                    <span
                                        class="section-label"
                                    >
                                        ${escapeHtml(
                                            prettyKey(key)
                                        )}
                                    </span>

                                    ${renderValue(
                                        value
                                    )}

                                </div>

                            `;

                        }
                    )
                    .join("")
            }

        </div>

    `;

}



/* =====================================================
   DASHBOARD
===================================================== */

function updateDashboardStats() {

    setText(
        "resumeStat",
        String(
            resumeItems.length
        )
    );


    setText(
        "jobStat",
        String(
            jobItems.length
        )
    );

}



/* =====================================================
   RESUME
===================================================== */

async function analyzeResume() {

    const input =
        document.getElementById(
            "resumeFile"
        );


    if (
        !input?.files?.length
    ) {

        showToast(
            "Please choose a resume PDF first."
        );

        return;

    }


    const file =
        input.files[0];


    if (
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        showToast(
            "Please select a PDF file."
        );

        return;

    }


    const form =
        new FormData();


    form.append(
        "file",
        file
    );


    const result =
        document.getElementById(
            "resumeResult"
        );


    if (result) {

        result.innerHTML = `

            <div class="loading-state">
                Analyzing your resume with AI...
            </div>

        `;

    }


    try {

        const data =
            await apiFetch(
                "/api/resume/analyze",
                {
                    method:"POST",
                    body:form
                }
            );


        currentResumeId =
            data.id ||
            data.resume_id ||
            null;


        renderAnalysis(
            "resumeResult",
            data
        );


        await loadSavedResumes();


        showToast(
            "Resume analyzed successfully."
        );

    }

    catch (error) {

        if (result) {

            result.innerHTML = `

                <div class="error-state">
                    ${escapeHtml(
                        error.message
                    )}
                </div>

            `;

        }

    }

}



/* =====================================================
   JOB
===================================================== */

async function analyzeJob() {

    const input =
        document.getElementById(
            "jobFile"
        );


    if (
        !input?.files?.length
    ) {

        showToast(
            "Please choose a job description PDF first."
        );

        return;

    }


    const file =
        input.files[0];


    if (
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        showToast(
            "Please select a PDF file."
        );

        return;

    }


    const form =
        new FormData();


    form.append(
        "file",
        file
    );


    const result =
        document.getElementById(
            "jobResult"
        );


    if (result) {

        result.innerHTML = `

            <div class="loading-state">
                Analyzing the job description with AI...
            </div>

        `;

    }


    try {

        const data =
            await apiFetch(
                "/api/job/analyze",
                {
                    method:"POST",
                    body:form
                }
            );


        currentJobId =
            data.id ||
            data.job_id ||
            null;


        renderAnalysis(
            "jobResult",
            data
        );


        await loadSavedJobs();


        showToast(
            "Job description analyzed successfully."
        );

    }

    catch (error) {

        if (result) {

            result.innerHTML = `

                <div class="error-state">
                    ${escapeHtml(
                        error.message
                    )}
                </div>

            `;

        }

    }

}



/* =====================================================
   SAVED RESUMES
===================================================== */

async function loadSavedResumes() {

    try {

        const data =
            await apiFetch(
                "/api/resume/list"
            );


        resumeItems =
            Array.isArray(data)
                ? data
                : (
                    data?.resumes ||
                    []
                );


        renderSavedResumes();

        populateSelectors();

        updateDashboardStats();

    }

    catch (error) {

        console.warn(
            "Resume list unavailable:",
            error.message
        );


        resumeItems = [];

        renderSavedResumes();

        populateSelectors();

    }

}



function renderSavedResumes() {

    const container =
        document.getElementById(
            "savedResumes"
        );


    if (!container) {
        return;
    }


    if (!resumeItems.length) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ▣
                </div>

                <h3>
                    No saved resumes yet
                </h3>

                <p>
                    Analyze a resume to add
                    it to your personal library.
                </p>

            </div>

        `;

        return;
    }


    /*
     * Remove duplicate entries from the UI.
     *
     * The backend returns newest records first,
     * therefore the first occurrence is kept.
     *
     * Primary comparison:
     * resume text.
     *
     * Fallback:
     * filename.
     */

    const uniqueResumes = [];

    const seenTexts = new Set();

    const seenNames = new Set();


    resumeItems.forEach(
        function (item) {

            const id =
                item.id ||
                item.resume_id;


            const filename =
                (
                    item.filename ||
                    ""
                )
                .trim()
                .toLowerCase();


            /*
             * If list endpoint contains resume_text,
             * use it for stronger duplicate detection.
             */

            const resumeText =
                (
                    item.resume_text ||
                    ""
                )
                .trim()
                .toLowerCase();


            if (
                resumeText &&
                seenTexts.has(resumeText)
            ) {

                return;

            }


            /*
             * If resume_text isn't returned,
             * use filename as fallback.
             */

            if (
                !resumeText &&
                filename &&
                seenNames.has(filename)
            ) {

                return;

            }


            if (resumeText) {

                seenTexts.add(
                    resumeText
                );

            }


            if (filename) {

                seenNames.add(
                    filename
                );

            }


            uniqueResumes.push(
                item
            );

        }
    );


    container.innerHTML =
        uniqueResumes
            .map(
                function (item) {

                    const id =
                        item.id ||
                        item.resume_id;


                    const filename =
                        item.filename ||
                        `Resume #${id}`;


                    return `

                        <div
                            class="saved-resume-card"
                        >

                            <div
                                class="saved-resume-icon"
                            >
                                ▤
                            </div>


                            <div>

                                <h3>
                                    ${escapeHtml(
                                        filename
                                    )}
                                </h3>

                                <p>
                                    Resume ID: ${id}
                                </p>

                            </div>


                            <div
                                class="resume-card-actions"
                            >

                                <button
                                    class="secondary-button"
                                    onclick="selectResume(${id})"
                                >
                                    Use
                                </button>


                                <button
                                    class="delete-resume"
                                    onclick="deleteResume(${id}, '${escapeHtml(filename).replaceAll("'", "\\'")}')"
                                >
                                    Delete
                                </button>

                            </div>


                        </div>

                    `;

                }
            )
            .join("");

}

async function deleteResume(
    resumeId,
    filename
) {

    const confirmed =
        window.confirm(
            `Delete "${filename}"?\n\nThis action cannot be undone.`
        );


    if (!confirmed) {
        return;
    }


    try {

        await apiFetch(
            `/api/resume/${resumeId}`,
            {
                method: "DELETE"
            }
        );


        if (
            Number(currentResumeId) ===
            Number(resumeId)
        ) {

            currentResumeId =
                null;

        }


        showToast(
            "Resume deleted successfully."
        );


        await loadSavedResumes();

    }

    catch (error) {

    if (
        error.message &&
        error.message.includes("404")
    ) {

        await loadSavedResumes();

        showToast(
            "Resume was already deleted."
        );

        return;
    }

    showToast(
        error.message ||
        "Failed to delete resume."
    );

}

}

async function removeDuplicateResumes() {

    const confirmed =
        window.confirm(
            "Remove duplicate resumes?\n\nThe newest copy of each identical resume will be kept."
        );


    if (!confirmed) {
        return;
    }


    try {

        const result =
            await apiFetch(
                "/api/resume/duplicates/cleanup",
                {
                    method: "DELETE"
                }
            );


        showToast(
            result.message ||
            "Duplicate resumes removed."
        );


        await loadSavedResumes();

    }

    catch (error) {

        showToast(
            error.message ||
            "Failed to remove duplicates."
        );

    }

}


function selectResume(
    id
) {

    currentResumeId =
        Number(id);


    populateSelectors();


    showPage(
        "matching"
    );

}



/* =====================================================
   SAVED JOBS
===================================================== */

async function loadSavedJobs() {

    try {

        const data =
            await apiFetch(
                "/api/job/list"
            );


        jobItems =
            Array.isArray(data)
                ? data
                : (
                    data?.jobs ||
                    []
                );


        populateSelectors();

        updateDashboardStats();

    }

    catch (error) {

        console.warn(
            "Job list unavailable:",
            error.message
        );


        jobItems = [];

        populateSelectors();

    }

}



/* =====================================================
   SELECTORS
===================================================== */

function populateSelectors() {

    const resumeSelect =
        document.getElementById(
            "matchingResume"
        );


    if (resumeSelect) {

        const previous =
            resumeSelect.value ||
            currentResumeId ||
            "";


        resumeSelect.innerHTML = `

            <option value="">
                Select analyzed resume
            </option>

        `;


        resumeItems.forEach(
            function (item) {

                const id =
                    item.id ||
                    item.resume_id;


                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    id;


                option.textContent =
                    item.filename ||
                    `Resume #${id}`;


                resumeSelect.appendChild(
                    option
                );

            }
        );


        if (previous) {

            resumeSelect.value =
                String(previous);

        }

    }



    const jobSelect =
        document.getElementById(
            "matchingJob"
        );


    if (jobSelect) {

        const previous =
            jobSelect.value ||
            currentJobId ||
            "";


        jobSelect.innerHTML = `

            <option value="">
                Select analyzed job
            </option>

        `;


        jobItems.forEach(
            function (item) {

                const id =
                    item.id ||
                    item.job_id;


                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    id;


                option.textContent =
                    item.filename ||
                    `Job #${id}`;


                jobSelect.appendChild(
                    option
                );

            }
        );


        if (previous) {

            jobSelect.value =
                String(previous);

        }

    }

}



/* =====================================================
   MATCHING
===================================================== */

async function runMatching() {

    const resumeId =
        Number(
            document.getElementById(
                "matchingResume"
            )?.value
        );


    const jobId =
        Number(
            document.getElementById(
                "matchingJob"
            )?.value
        );


    const result =
        document.getElementById(
            "matchResult"
        );


    if (
        !resumeId ||
        !jobId
    ) {

        showToast(
            "Select both a resume and a job description."
        );

        return;

    }


    currentResumeId =
        resumeId;


    currentJobId =
        jobId;


    if (result) {

        result.classList.remove(
            "hidden"
        );


        result.innerHTML = `

            <div class="loading-state">
                Calculating your career fit...
            </div>

        `;

    }


    try {

        const data =
            await apiFetch(
                "/api/matching/analyze",
                {

                    method:"POST",

                    body:
                        JSON.stringify({

                            resume_id:
                                resumeId,

                            job_id:
                                jobId

                        })

                }
            );


        renderMatchResult(
            data
        );


        setText(
            "matchStat",
            "1"
        );


        showToast(
            "Career match created."
        );

    }

    catch (error) {

        if (result) {

            result.innerHTML = `

                <div class="error-state">
                    ${escapeHtml(
                        error.message
                    )}
                </div>

            `;

        }

    }

}



function renderMatchResult(
    data
) {

    let result =
    data?.matching ||
    data?.result ||
    data?.result_json ||
    data;

    /*
     * Backend may return result_json
     * as a JSON string.
     * Convert it into an object before rendering.
     */
    if (typeof result === "string") {
        try {
            result = JSON.parse(result);
        }
        catch (error) {
            console.error(
                "Failed to parse matching result:",
                error
            );
            result = {};
        }
    }

    const score =
        Number(
            result?.match_score ?? 0
        );

    const resultBox =
        document.getElementById(
            "matchResult"
        );

    if (!resultBox) {
        return;
    }

    resultBox.innerHTML = `

        <div class="panel-header">

            <div>

                <span class="section-label">
                    AI RESULT
                </span>

                <h3>
                    Career Fit Analysis
                </h3>

            </div>

        </div>


        <div class="match-score">

            <span>
                Career Match
            </span>

            <strong>
                ${Math.round(score)}%
            </strong>

        </div>


        <div class="ai-result">

            ${renderMatchCard(
                "Matched Skills",
                result?.matched_skills
            )}

            ${renderMatchCard(
                "Missing Required Skills",
                result?.missing_required_skills
            )}

            ${renderMatchCard(
                "Missing Preferred Skills",
                result?.missing_preferred_skills
            )}

            ${renderMatchCard(
                "Strong Areas",
                result?.strong_areas
            )}

            ${renderMatchCard(
                "Weak Areas",
                result?.weak_areas
            )}

            ${renderMatchCard(
                "Interview Priorities",
                result?.interview_priorities
            )}

            ${renderMatchCard(
                "Learning Priorities",
                result?.learning_priorities
            )}

            ${renderMatchCard(
                "Experience Match",
                result?.experience_match
            )}

            ${renderMatchCard(
                "Education Match",
                result?.education_match
            )}

            ${renderMatchCard(
                "Recommendation",
                result?.recommendation
            )}

        </div>

    `;
}


function renderMatchCard(
    title,
    value
) {

    return `

        <div class="ai-result-card">

            <span class="section-label">
                ${escapeHtml(title)}
            </span>

            ${renderValue(value)}

        </div>

    `;

}



/* =====================================================
   INTERVIEW
===================================================== */

async function startInterview() {

    const resumeId =
        currentResumeId ||
        Number(
            document.getElementById(
                "matchingResume"
            )?.value
        );


    const jobId =
        currentJobId ||
        Number(
            document.getElementById(
                "matchingJob"
            )?.value
        );


    const difficulty =
        document.getElementById(
            "difficulty"
        )?.value ||
        "medium";


    if (
        !resumeId ||
        !jobId
    ) {

        showToast(
            "Analyze/select a resume and job before starting the interview."
        );

        return;

    }


    try {

        const data =
            await apiFetch(
                "/api/interview/start",
                {

                    method:"POST",

                    body:
                        JSON.stringify({

                            resume_id:
                                resumeId,

                            job_id:
                                jobId,

                            difficulty:
                                difficulty

                        })

                }
            );


        currentInterviewSessionId =
            data.session_id ||
            data.id;


        currentQuestionId =
            data.question_id;


        currentQuestionNumber =
            data.question_number ||
            1;


        setText(
            "interviewResumeLabel",
            `Resume #${resumeId}`
        );


        setText(
            "interviewJobLabel",
            `Job #${jobId}`
        );


        document
            .getElementById(
                "interviewSetup"
            )
            ?.classList.add(
                "hidden"
            );


        document
            .getElementById(
                "interviewPanel"
            )
            ?.classList.remove(
                "hidden"
            );


        document
            .getElementById(
                "evaluationPanel"
            )
            ?.classList.add(
                "hidden"
            );


        document
            .getElementById(
                "finalReport"
            )
            ?.classList.add(
                "hidden"
            );


        renderQuestion(
            data
        );


        showToast(
            "AI interview started."
        );

    }

    catch (error) {

        showToast(
            error.message
        );

    }

}



function renderQuestion(
    data
) {

    setText(
        "questionText",
        data.question ||
        data.question_text ||
        "No question returned."
    );


    setText(
        "questionCounter",
        `Question ${
            data.question_number ||
            currentQuestionNumber
        }`
    );


    const answer =
        document.getElementById(
            "answerInput"
        );


    if (answer) {

        answer.value =
            "";

        answer.focus();

    }

}



async function submitAnswer() {

    const answer =
        document.getElementById(
            "answerInput"
        )?.value.trim();


    if (!answer) {

        showToast(
            "Enter your answer first."
        );

        return;

    }


    if (
        !currentInterviewSessionId ||
        !currentQuestionId
    ) {

        showToast(
            "Interview session is not active."
        );

        return;

    }


    try {

        const data =
            await apiFetch(
                "/api/interview/answer",
                {

                    method:"POST",

                    body:
                        JSON.stringify({

                            session_id:
                                currentInterviewSessionId,

                            question_id:
                                currentQuestionId,

                            answer:
                                answer

                        })

                }
            );


        renderEvaluation(
            data.evaluation ||
            data.evaluation_json ||
            data
        );


        if (
            data.question ||
            data.next_question
        ) {

            currentQuestionId =
                data.question_id ||
                data.next_question_id ||
                currentQuestionId;


            currentQuestionNumber =
                data.question_number ||
                (
                    currentQuestionNumber +
                    1
                );


            renderQuestion({

                question:
                    data.question ||
                    data.next_question,

                question_number:
                    currentQuestionNumber

            });

        }

        else {

            showToast(
                "Answer evaluated. Continue or finish the interview."
            );

        }

    }

    catch (error) {

        showToast(
            error.message
        );

    }

}



function renderEvaluation(
    evaluation
) {

    const panel =
        document.getElementById(
            "evaluationPanel"
        );


    const content =
        document.getElementById(
            "evaluationContent"
        );


    if (
        !panel ||
        !content
    ) {

        return;

    }


    panel.classList.remove(
        "hidden"
    );


    content.innerHTML =
        renderValue(
            evaluation
        );

}



/* =====================================================
   FINISH INTERVIEW
===================================================== */

async function finishInterview() {

    if (
        !currentInterviewSessionId
    ) {

        showToast(
            "No active interview."
        );

        return;

    }


    try {

        const data =
            await apiFetch(
                "/api/interview/finish",
                {

                    method:"POST",

                    body:
                        JSON.stringify({

                            session_id:
                                currentInterviewSessionId

                        })

                }
            );


        const report =
            data?.report ||
            data?.result ||
            data;


        const panel =
            document.getElementById(
                "finalReport"
            );


        const content =
            document.getElementById(
                "reportContent"
            );


        if (
            panel &&
            content
        ) {

            panel.classList.remove(
                "hidden"
            );


            content.innerHTML =
                renderValue(
                    report
                );

        }


        document
            .getElementById(
                "interviewPanel"
            )
            ?.classList.add(
                "hidden"
            );


        document
            .getElementById(
                "evaluationPanel"
            )
            ?.classList.add(
                "hidden"
            );


        setText(
            "interviewStat",
            "1"
        );


        showToast(
            "Interview completed."
        );

    }

    catch (error) {

        showToast(
            error.message
        );

    }

}



/* =====================================================
   FILE INPUTS
===================================================== */

function bindFileInputs() {

    const resumeInput =
        document.getElementById(
            "resumeFile"
        );


    if (resumeInput) {

        resumeInput.addEventListener(
            "change",
            function () {

                setText(
                    "resumeFileName",
                    resumeInput.files?.[0]
                        ?.name ||
                    "No file selected"
                );

            }
        );

    }


    const jobInput =
        document.getElementById(
            "jobFile"
        );


    if (jobInput) {

        jobInput.addEventListener(
            "change",
            function () {

                setText(
                    "jobFileName",
                    jobInput.files?.[0]
                        ?.name ||
                    "No file selected"
                );

            }
        );

    }

}



/* =====================================================
   INITIALIZATION
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        restoreSidebarState();

        bindFileInputs();


        document
            .querySelectorAll(
                ".nav-item"
            )
            .forEach(
                function (item) {

                    item.addEventListener(
                        "click",
                        function () {

                            showPage(
                                item.dataset.page
                            );

                        }
                    );

                }
            );


        await loadSavedResumes();

        await loadSavedJobs();


        showPage(
            "dashboard"
        );

    }
);
