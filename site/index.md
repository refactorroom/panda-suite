<section class="home-wrap home-hero" aria-labelledby="home-title">
  <div>
    <h1 id="home-title">Engineering skills for your coding agent.</h1>
    <p class="home-intro">Plan a change, investigate a bug, review a diff, or write a guide. Ask Panda Lead to choose a workflow, or go straight to the specialist you need.</p>
    <div class="home-ctas">
      <a class="home-button primary" href="#quick-start">Get started</a>
      <a class="home-button" href="skills.html">Browse {{skill_count}} skills</a>
    </div>
  </div>
  <figure class="home-terminal" id="your-first-request">
    <figcaption><span>Codex plugin prompt</span></figcaption>
    <pre data-copy-label="Copy Codex plugin prompt"><code>$panda-suite:panda-lead Explain how orders are created in this project. Use the source as evidence and keep the repository read-only.</code></pre>
    <p>Panda Lead can route this request to <a href="panda-learn.html">Panda Learn</a> for a source walkthrough.</p>
  </figure>
</section>

<section id="quick-start" class="home-band home-section" aria-labelledby="quick-heading">
  <div class="home-wrap">
    <h2 id="quick-heading">Quick start</h2>
    <div class="home-grid">
      <article class="home-card">
        <h3>Install the plugin</h3>
        <p>Use the GitHub release for the v{{version}} skill set. Clone it, then follow the instructions for your host.</p>
        <pre data-copy-label="Copy plugin checkout commands"><code>git clone --branch v{{version}} https://github.com/refactorroom/panda-suite.git
cd panda-suite</code></pre>
        <p class="home-links"><a href="installation.html#openai-codex">Install in Codex</a><a href="installation.html#claude-code">Load in Claude Code</a></p>
      </article>
      <article class="home-card">
        <h3>Install a standalone skill</h3>
        <p>With Node.js 20+, run this from the project where you want Codex to discover the skill.</p>
        <pre data-copy-label="Copy standalone install command"><code>npx --yes panda-suite@latest install --skill panda-lead --destination .agents/skills</code></pre>
        <p>Refresh your host, then select <code>panda-lead</code>. The npm package may lag behind the GitHub release.</p>
        <p><a href="usage.html#invoke-a-skill">See invocation formats for each host</a></p>
      </article>
    </div>
  </div>
</section>

<section class="home-wrap home-section" id="choose-the-task-then-the-skill" aria-labelledby="workflow-heading">
  <div class="home-section-head">
    <h2 id="workflow-heading">Choose a workflow</h2>
    <a href="skills.html">View the full skill directory</a>
  </div>
  <div class="home-workflows">
    <a href="panda-lead.html"><strong>Ask Panda Lead</strong><span>Get help choosing the skills and sequence your request needs.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
    <a href="panda-plan.html"><strong>Plan a change</strong><span>Turn an agreed scope into ordered tasks, dependencies, and checks.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
    <a href="panda-execute.html"><strong>Implement agreed work</strong><span>Make scoped changes and verify them against the acceptance criteria.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
    <a href="panda-debugger.html"><strong>Investigate a failure</strong><span>Trace unexpected behavior and verify the cause against the evidence.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
    <a href="panda-review.html"><strong>Review a diff</strong><span>Find material defects and explain their triggers and impact.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
    <a href="panda-write.html"><strong>Write a guide</strong><span>Document setup, workflows, and errors from the implementation and tests.</span><span class="workflow-arrow" aria-hidden="true">↗</span></a>
  </div>
</section>

<section class="home-band home-section" id="reference" aria-labelledby="reference-heading">
  <div class="home-wrap home-grid">
    <div>
      <h2 id="reference-heading">Find a guide</h2>
      <p>Look up a skill, task, or command across the docs.</p>
      <form role="search" id="search-form">
        <label for="search">Search the docs</label>
        <div class="search-box"><input id="search" type="search" placeholder="Try panda-write or compare" autocomplete="off" aria-controls="search-results"></div>
      </form>
      <div id="search-status" class="sr-only" role="status"></div>
      <div id="search-results" hidden></div>
    </div>
    <div class="home-resources">
      <div><h3>Use an existing skill</h3><p><a href="usage.html">Complete usage guide</a> · <a href="routing.html">Routing rules</a></p></div>
      <div><h3>Verify an outcome</h3><p><a href="panda-invaris.html">Invaris checks and campaigns</a> · <a href="panda-evaris.html">Evaris evaluations</a></p></div>
      <div id="latest-release-v1-9-0"><h3>GitHub release v{{version}}</h3><p><a href="https://github.com/refactorroom/panda-suite/releases/tag/v{{version}}">Release notes</a> · <a href="verification.html">Verification record</a></p></div>
    </div>
  </div>
</section>
