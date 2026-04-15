import React from 'react'
import ReadinessProgression from '../readiness/ReadinessProgression'

const IRLProgression = ({ cteId, currentIRL, onIRLUpdated }) => (
  <ReadinessProgression cteId={cteId} domain="irl" currentLevel={currentIRL} onUpdated={onIRLUpdated} />
)

export default IRLProgression
