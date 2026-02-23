import React from 'react'
import { Link } from 'react-router-dom'
import { FiTarget, FiLayers, FiShield, FiTrendingUp, FiCheckCircle, FiBarChart2, FiUsers, FiFileText, FiLock } from 'react-icons/fi'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'

const LandingPage = () => {
  // Sample data for subtle infographics
  const trlDistribution = [
    { level: 'TRL 1-3', count: 12, color: '#C44536' },
    { level: 'TRL 4-6', count: 28, color: '#D4A017' },
    { level: 'TRL 7-9', count: 45, color: '#2E7D32' },
  ]

  const featureStats = [
    { label: 'Projects Tracked', value: '150+', icon: FiTarget },
    { label: 'CTEs Monitored', value: '450+', icon: FiLayers },
    { label: 'Active Users', value: '85+', icon: FiUsers },
    { label: 'Assessments', value: '1.2K+', icon: FiCheckCircle },
  ]

  const capabilities = [
    {
      icon: FiTarget,
      title: 'TRL Tracking',
      description: 'Comprehensive Technology Readiness Level assessment and progression tracking across all project dimensions.',
      color: 'primary-600',
    },
    {
      icon: FiLayers,
      title: 'CTE Management',
      description: 'Manage Critical Technology Elements with granular readiness tracking and evidence-based assessments.',
      color: 'primary-600',
    },
    {
      icon: FiBarChart2,
      title: 'Portfolio Analytics',
      description: 'Real-time dashboards and infographics showing project health, risk levels, and readiness distribution.',
      color: 'primary-600',
    },
    {
      icon: FiShield,
      title: 'Role-Based Access',
      description: 'Hierarchical permissions ensuring secure, role-appropriate access to projects and assessments.',
      color: 'primary-600',
    },
    {
      icon: FiFileText,
      title: 'Evidence Management',
      description: 'Attach files, links, and documentation to TRL responses with configurable evidence requirements.',
      color: 'primary-600',
    },
    {
      icon: FiTrendingUp,
      title: 'Multi-Dimensional Readiness',
      description: 'Track TRL, IRL, MRL, and SRL across technology elements for comprehensive maturity assessment.',
      color: 'primary-600',
    },
  ]

  return (
    <div className="min-h-screen bg-shell-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20">
          <div className="text-center">
            {/* Logo */}
            <div className="inline-flex items-center justify-center h-20 w-20 bg-primary-700 rounded-md mb-6 shadow-lg">
              <span className="text-white font-bold text-3xl tracking-wide">TRI</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight mb-4">
              Trilokya
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-2 font-medium">
              Technology Readiness Level Monitoring System
            </p>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-10">
              Comprehensive project oversight and maturity tracking for defense research and development initiatives
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/login"
                className="btn-primary text-base px-8 py-3 min-h-[52px]"
              >
                Sign In to System
              </Link>
              <a
                href="#features"
                className="btn-secondary text-base px-8 py-3 min-h-[52px]"
              >
                Learn More
              </a>
            </div>
          </div>
        </div>

        {/* Subtle background pattern */}
        <div className="absolute inset-0 -z-10 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, #146c6c 1px, transparent 0)`,
            backgroundSize: '40px 40px'
          }} />
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-y" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {featureStats.map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="text-center">
                  <div className="inline-flex items-center justify-center h-12 w-12 rounded bg-primary-50 mb-3">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <p className="text-2xl md:text-3xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1">{stat.label}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Project Monitoring
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built for defense research organizations requiring rigorous technology readiness assessment and governance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((cap, idx) => {
              const Icon = cap.icon
              return (
                <div key={idx} className="card p-6 hover:shadow-md transition-shadow duration-200">
                  <div className="h-12 w-12 rounded bg-primary-50 flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{cap.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{cap.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Infographics Section */}
      <section className="py-20" style={{ backgroundColor: '#f0f6f6' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              System Capabilities
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Visual insights into project readiness and technology maturity tracking
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* TRL Distribution Chart */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">TRL Distribution</h3>
              <p className="text-sm text-gray-500 mb-6">
                Typical distribution of technology readiness levels across active projects
              </p>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={trlDistribution}>
                  <XAxis dataKey="level" tick={{ fontSize: 11, fill: '#6B7280' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {trlDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Readiness Dimensions */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Multi-Dimensional Readiness</h3>
              <p className="text-sm text-gray-500 mb-6">
                Track technology maturity across multiple readiness dimensions
              </p>
              <div className="space-y-4">
                {[
                  { label: 'TRL', desc: 'Technology Readiness Level', progress: 75, color: '#146c6c' },
                  { label: 'IRL', desc: 'Integration Readiness Level', progress: 60, color: '#1f8a8a' },
                  { label: 'MRL', desc: 'Manufacturing Readiness Level', progress: 45, color: '#4f9797' },
                  { label: 'SRL', desc: 'System Readiness Level', progress: 55, color: '#8cbfbf' },
                ].map((dim) => (
                  <div key={dim.label} className="space-y-1.5">
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="font-semibold text-gray-900">{dim.label}</span>
                        <span className="text-gray-500 ml-2 text-xs">— {dim.desc}</span>
                      </div>
                      <span className="font-bold text-gray-700">{dim.progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${dim.progress}%`, backgroundColor: dim.color }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Why Trilokya?
              </h2>
              <div className="space-y-4">
                {[
                  {
                    title: 'Evidence-Based Assessment',
                    desc: 'Every TRL progression requires documented evidence, ensuring accountability and traceability.',
                  },
                  {
                    title: 'Real-Time Portfolio Health',
                    desc: 'Comprehensive dashboards provide instant visibility into project status and risk levels.',
                  },
                  {
                    title: 'Configurable Workflows',
                    desc: 'Flexible approval processes and role-based access control tailored to your organization.',
                  },
                  {
                    title: 'Audit Trail',
                    desc: 'Complete history of assessments, approvals, and configuration changes for compliance.',
                  },
                ].map((benefit, idx) => (
                  <div key={idx} className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded bg-primary-50 flex items-center justify-center">
                        <FiCheckCircle className="h-4 w-4 text-primary-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{benefit.title}</h3>
                      <p className="text-sm text-gray-600">{benefit.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-8">
              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded bg-primary-50 flex items-center justify-center">
                    <FiLock className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Secure & Compliant</h3>
                    <p className="text-sm text-gray-600">Built with defense-grade security standards</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded bg-primary-50 flex items-center justify-center">
                    <FiTrendingUp className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Scalable Architecture</h3>
                    <p className="text-sm text-gray-600">Handles projects of any size and complexity</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded bg-primary-50 flex items-center justify-center">
                    <FiBarChart2 className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Data-Driven Insights</h3>
                    <p className="text-sm text-gray-600">Advanced analytics and reporting capabilities</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20" style={{ backgroundColor: '#f0f6f6' }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Access the Trilokya Project Monitoring System to begin tracking your technology readiness
          </p>
          <Link
            to="/login"
            className="btn-primary text-base px-10 py-4 min-h-[56px] inline-flex items-center justify-center"
          >
            Sign In to System
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8" style={{ borderColor: '#D9E2E2' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded bg-primary-700 flex items-center justify-center">
                <span className="text-white font-bold text-sm tracking-wide">TRI</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">Trilokya v1.0</span>
            </div>
            <p className="text-xs text-gray-500">
              Technology Readiness Level Monitoring System — Defense Research & Development
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
