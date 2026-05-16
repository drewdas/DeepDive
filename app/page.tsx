export default function Home() {
  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">
          DeepDive: Advancing Deep Search Agents with Knowledge Graphs and Multi-Turn RL
        </h1>
        
        <div className="mb-8 flex gap-4">
          <a 
            href="https://github.com/THUDM/DeepDive" 
            className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a 
            href="https://arxiv.org/pdf/2509.10446" 
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            target="_blank"
            rel="noopener noreferrer"
          >
            arXiv Paper
          </a>
          <a 
            href="https://huggingface.co/datasets/zai-org/DeepDive" 
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            target="_blank"
            rel="noopener noreferrer"
          >
            Dataset
          </a>
        </div>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Overview</h2>
          <p className="text-gray-700 leading-relaxed">
            DeepDive presents an automated approach for training deep search agents that can navigate complex, 
            multi-step information-seeking tasks. Our method combines automated data synthesis from knowledge 
            graphs with end-to-end multi-turn reinforcement learning to create agents capable of sophisticated 
            long-horizon reasoning and web browsing.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>Automated Deep Search Data Synthesis from knowledge graphs</li>
            <li>Multi-Turn RL Training for sophisticated browsing capabilities</li>
            <li>Test-Time Scaling via tool calls and parallel sampling</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">News</h2>
          <ul className="space-y-2 text-gray-700">
            <li><strong>[2025/10/02]</strong> Released the complete data construction pipeline</li>
            <li><strong>[2025/09/17]</strong> QA pairs and SFT trajectories fully open-sourced (4,108 entries)</li>
            <li>Model and code currently under development – coming soon!</li>
          </ul>
        </section>

        <footer className="mt-12 pt-8 border-t border-gray-200 text-sm text-gray-600">
          <p>
            For more information, visit the{" "}
            <a href="https://github.com/THUDM/DeepDive" className="text-blue-600 hover:underline">
              GitHub repository
            </a>
            {" "}or read the{" "}
            <a href="https://arxiv.org/pdf/2509.10446" className="text-blue-600 hover:underline">
              full paper
            </a>
            .
          </p>
        </footer>
      </main>
    </div>
  );
}
