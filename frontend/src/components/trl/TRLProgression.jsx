import React from 'react'
import ReadinessProgression from '../readiness/ReadinessProgression'

const TRLProgression = ({ cteId, currentTRL, onTRLUpdated }) => (
  <ReadinessProgression cteId={cteId} domain="trl" currentLevel={currentTRL} onUpdated={onTRLUpdated} />
)

export default TRLProgression
