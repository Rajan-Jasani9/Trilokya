import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'

const TRLAssessment = ({ cteId, trlLevel }) => {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQuestions()
  }, [cteId, trlLevel])

  const loadQuestions = async () => {
    try {
      const response = await api.get(`/trl/ctes/${cteId}/trl-assessments/${trlLevel}/questions`)
      setQuestions(response.data)
    } catch (error) {
      console.error('Error loading questions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">TRL Level {trlLevel} Assessment</h2>
      <div className="space-y-4">
        {questions.map((question) => (
          <div key={question.id} className="bg-white rounded-lg shadow p-4 md:p-6">
            <h3 className="font-medium text-gray-900 mb-4">{question.question_text}</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input type="radio" name={`question-${question.id}`} value="Yes" className="h-5 w-5" />
                <span className="text-sm text-gray-700">Yes</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="radio" name={`question-${question.id}`} value="No" className="h-5 w-5" />
                <span className="text-sm text-gray-700">No</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="radio" name={`question-${question.id}`} value="NA" className="h-5 w-5" />
                <span className="text-sm text-gray-700">Not Applicable</span>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TRLAssessment
