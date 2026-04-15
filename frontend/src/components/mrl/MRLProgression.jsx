import React from 'react'
import ReadinessProgression from '../readiness/ReadinessProgression'

const MRLProgression = ({ cteId, currentMRL, onMRLUpdated }) => (
  <ReadinessProgression cteId={cteId} domain="mrl" currentLevel={currentMRL} onUpdated={onMRLUpdated} />
)

export default MRLProgression
