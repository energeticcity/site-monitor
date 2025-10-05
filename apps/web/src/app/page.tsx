export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">SiteWatcher</h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Multi-tenant SaaS for detecting new posts on websites
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/auth/signin"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </a>
          <a
            href="/docs"
            className="px-6 py-3 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            Documentation
          </a>
        </div>
      </div>
    </main>
  );
}

