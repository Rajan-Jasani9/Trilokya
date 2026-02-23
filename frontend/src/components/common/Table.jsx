import React from 'react'

const ResponsiveTable = ({ columns, data, renderRow, renderCard }) => {
  return (
    <>
      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto">
        <div className="card overflow-hidden">
          <table className="min-w-full divide-y" style={{ borderColor: '#D9E2E2' }}>
            <thead style={{ backgroundColor: '#f0f6f6' }}>
              <tr>
                {columns.map((col, idx) => (
                  <th
                    key={idx}
                    className="px-5 py-3 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider"
                  >
                    {col.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y" style={{ borderColor: '#D9E2E2' }}>
              {data.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-primary-50/40 transition-colors duration-100"
                >
                  {renderRow(row, rowIdx)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {data.map((row, rowIdx) => (
          <div key={rowIdx} className="card p-4">
            {renderCard(row, rowIdx)}
          </div>
        ))}
      </div>
    </>
  )
}

export default ResponsiveTable
