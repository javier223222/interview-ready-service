# 📋 Interview Ready API - Endpoints Documentation

## 🔗 Base URL
```
https://teching.tech/interviewready/api/v1
```

## 🔐 Authentication
All endpoints require Bearer token authentication:
```http
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

---

## 📊 Endpoints Summary

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| POST | `/interview/questions/generate` | Generate interview questions | 201 |
| POST | `/interview/questions/response/{id}` | Submit answer to question | 200 |
| GET | `/interview/questions/feedback/{id}` | Get interview feedback | 200 |
| GET | `/interview/history/{user_id}` | Get user interview history | 200 |
| GET | `/interview/history/{user_id}/{interview_id}` | Get specific interview details | 200 |

---

## 🚀 1. Generate Interview Questions

### **POST** `/interview/questions/generate`

**Full URL**: `https://teching.tech/interviewready/api/v1/interview/questions/generate`

**Description**: Creates a new interview session with AI-generated questions based on user profile.

**Headers**:
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "user_seniority": "senior",
  "user_specialization": "backend",
  "type": "technical",
  "question_number": {
    "value": 10
  }
}
```

**Request Parameters**:
- `user_id` (string, required): MongoDB ObjectId format (24 hex characters)
- `user_seniority` (string, required): One of `["junior", "mid", "senior", "lead", "principal"]`
- `user_specialization` (string, required): Technical specialization (e.g., "backend", "frontend", "mobile")
- `type` (string, required): One of `["behavioral", "structured", "technical", "simulation"]`
- `question_number` (object, required): `{"value": number}` where number is one of `[5, 10, 15, 30]`

**Success Response (201 Created)**:
```json
{
  "id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "user_id": "507f1f77bcf86cd799439011",
  "type": "technical",
  "current_question": {
    "id": 1,
    "question": "Explain the difference between SQL and NoSQL databases...",
    "answer": null,
    "feedback": null,
    "competency": "Database Design",
    "difficulty": "intermediate"
  },
  "next_question": {
    "id": 2,
    "question": "How would you optimize a slow-performing query?",
    "answer": null,
    "feedback": null,
    "competency": "Performance Optimization",
    "difficulty": "advanced"
  },
  "init_at": "2025-01-15T10:30:00.000Z",
  "status": "in_progress",
  "question_number": 10,
  "actual_question": 1,
  "feedback": null,
  "message": "Interview session created successfully"
}
```

**Error Responses**:
```json
// 400 Bad Request
{
  "detail": "Seniority debe ser uno de: ['junior', 'mid', 'senior', 'lead', 'principal']"
}

// 422 Unprocessable Entity
{
  "detail": "Validation error: question_number.value must be one of [5, 10, 15, 30]"
}

// 500 Internal Server Error
{
  "detail": "An internal error occurred while generating questions"
}
```

---

## 💬 2. Submit Answer to Question

### **POST** `/interview/questions/response/{interview_id}`

**Full URL**: `https://teching.tech/interviewready/api/v1/interview/questions/response/{interview_id}?user_response={answer}&user_id={user_id}`

**Description**: Submits user's answer to the current question and advances interview progression.

**Headers**:
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters**:
- `interview_id` (string, required): The interview session ID

**Query Parameters**:
- `user_response` (string, required): The user's answer to the current question
- `user_id` (string, required): User identifier (MongoDB ObjectId format)

**Example Request**:
```http
POST https://teching.tech/interviewready/api/v1/interview/questions/response/60f7b3b3b3b3b3b3b3b3b3b3?user_response=I%20would%20use%20indexing%20and%20query%20optimization&user_id=507f1f77bcf86cd799439011
```

**Success Response (200 OK)**:
```json
{
  "id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "user_id": "507f1f77bcf86cd799439011",
  "type": "technical",
  "current_question": {
    "id": 1,
    "question": "Explain the difference between SQL and NoSQL databases...",
    "answer": "I would use indexing and query optimization",
    "feedback": "Good answer! You demonstrated understanding of optimization techniques.",
    "competency": "Database Design",
    "difficulty": "intermediate"
  },
  "next_question": {
    "id": 2,
    "question": "How would you optimize a slow-performing query?",
    "answer": null,
    "feedback": null,
    "competency": "Performance Optimization",
    "difficulty": "advanced"
  },
  "init_at": "2025-01-15T10:30:00.000Z",
  "status": "in_progress",
  "question_number": 10,
  "actual_question": 2,
  "feedback": "Good answer! You demonstrated understanding of optimization techniques.",
  "good_question": true
}
```

**Response when interview completes**:
```json
{
  "id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "user_id": "507f1f77bcf86cd799439011",
  "type": "technical",
  "current_question": {
    "id": 10,
    "question": "Last question...",
    "answer": "Final answer",
    "feedback": "Excellent conclusion!",
    "competency": "System Design",
    "difficulty": "advanced"
  },
  "next_question": null,
  "init_at": "2025-01-15T10:30:00.000Z",
  "status": "completed",
  "question_number": 10,
  "actual_question": 10,
  "feedback": "Excellent conclusion!",
  "good_question": true,
  "message": "Interview completed successfully"
}
```

**Error Responses**:
```json
// 400 Bad Request
{
  "detail": "Invalid interview ID or user ID"
}

// 404 Not Found
{
  "detail": "Interview not found"
}

// 422 Unprocessable Entity
{
  "detail": "Validation error: user_response is required"
}
```

---

## 📊 3. Get Interview Feedback

### **GET** `/interview/questions/feedback/{interview_id}`

**Full URL**: `https://teching.tech/interviewready/api/v1/interview/questions/feedback/{interview_id}?user_id={user_id}`

**Description**: Retrieves comprehensive AI-generated feedback after interview completion.

**Headers**:
```http
Authorization: Bearer <token>
```

**Path Parameters**:
- `interview_id` (string, required): The interview session ID

**Query Parameters**:
- `user_id` (string, required): User identifier

**Example Request**:
```http
GET https://teching.tech/interviewready/api/v1/interview/questions/feedback/60f7b3b3b3b3b3b3b3b3b3b3?user_id=507f1f77bcf86cd799439011
```

**Success Response (200 OK)**:
```json
{
  "interview_id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "user_id": "507f1f77bcf86cd799439011",
  "points_earned": 85,
  "feedback": {
    "overall_score": 85,
    "competency_breakdown": [
      {
        "name": "Database Design",
        "score": 90
      },
      {
        "name": "Performance Optimization",
        "score": 80
      },
      {
        "name": "System Architecture",
        "score": 85
      }
    ],
    "points_earned": 85,
    "focus_questions": [
      "Improve understanding of microservices architecture",
      "Practice more complex SQL optimization scenarios",
      "Study distributed system patterns"
    ],
    "summary_feedback": "Strong performance overall with excellent database knowledge. Consider focusing on distributed systems concepts for senior-level positions."
  },
  "init_at": "2025-01-15T10:30:00.000Z",
  "finish_at": "2025-01-15T11:15:00.000Z"
}
```

**Error Responses**:
```json
// 400 Bad Request
{
  "detail": "Interview not completed or invalid ID"
}

// 404 Not Found
{
  "detail": "Interview not found"
}
```

---

## 📜 4. Get User Interview History

### **GET** `/interview/history/{user_id}`

**Full URL**: `https://teching.tech/interviewready/api/v1/interview/history/{user_id}`

**Description**: Retrieves all interviews conducted by a specific user.

**Headers**:
```http
Authorization: Bearer <token>
```

**Path Parameters**:
- `user_id` (string, required): User identifier

**Example Request**:
```http
GET https://teching.tech/interviewready/api/v1/interview/history/507f1f77bcf86cd799439011
```

**Success Response (200 OK)**:
```json
{
  "interviews": [
    {
      "user_id": "507f1f77bcf86cd799439011",
      "user_seniority": "senior",
      "type": "technical",
      "user_specialization": "backend",
      "init_at": "2025-01-15T10:30:00.000Z",
      "end_at": "2025-01-15T11:15:00.000Z",
      "status": "completed",
      "questions_number": 10,
      "points_earned": 85,
      "updated_at": "2025-01-15T11:15:00.000Z",
      "id": "60f7b3b3b3b3b3b3b3b3b3b3"
    },
    {
      "user_id": "507f1f77bcf86cd799439011",
      "user_seniority": "senior",
      "type": "behavioral",
      "user_specialization": "backend",
      "init_at": "2025-01-14T14:20:00.000Z",
      "end_at": "2025-01-14T15:05:00.000Z",
      "status": "completed",
      "questions_number": 5,
      "points_earned": 78,
      "updated_at": "2025-01-14T15:05:00.000Z",
      "id": "60f7b3b3b3b3b3b3b3b3b3b4"
    }
  ],
  "total": 2
}
```

**Error Responses**:
```json
// 404 Not Found
{
  "detail": "No interview history found"
}

// 400 Bad Request
{
  "detail": "Invalid user ID format"
}
```

---

## 🔍 5. Get Specific Interview Details

### **GET** `/interview/history/{user_id}/{interview_id}`

**Full URL**: `https://teching.tech/interviewready/api/v1/interview/history/{user_id}/{interview_id}`

**Description**: Retrieves complete details of a specific interview including all questions and answers.

**Headers**:
```http
Authorization: Bearer <token>
```

**Path Parameters**:
- `user_id` (string, required): User identifier
- `interview_id` (string, required): Interview session ID

**Example Request**:
```http
GET https://teching.tech/interviewready/api/v1/interview/history/507f1f77bcf86cd799439011/60f7b3b3b3b3b3b3b3b3b3b3
```

**Success Response (200 OK)**:
```json
{
  "userId": "507f1f77bcf86cd799439011",
  "type": "technical",
  "user_seniority": "senior",
  "user_specialization": "backend",
  "questions": [
    {
      "id": 1,
      "question": "Explain the difference between SQL and NoSQL databases...",
      "answer": "SQL databases are relational and use structured tables...",
      "feedback": "Excellent explanation with clear examples!",
      "competency": "Database Design",
      "difficulty": "intermediate"
    },
    {
      "id": 2,
      "question": "How would you optimize a slow-performing query?",
      "answer": "I would start by analyzing the execution plan...",
      "feedback": "Good systematic approach to optimization.",
      "competency": "Performance Optimization",
      "difficulty": "advanced"
    }
  ],
  "init_at": "2025-01-15T10:30:00.000Z",
  "end_at": "2025-01-15T11:15:00.000Z",
  "status": "completed",
  "question_number": 10,
  "actual_question": null,
  "previus_question": {
    "id": 10,
    "question": "Design a scalable microservices architecture...",
    "answer": "I would use API Gateway, service discovery...",
    "feedback": "Comprehensive design with good scalability considerations.",
    "competency": "System Architecture",
    "difficulty": "advanced"
  },
  "points_earned": 85,
  "feedback": {
    "overall_score": 85,
    "competency_breakdown": [
      {
        "name": "Database Design",
        "score": 90
      },
      {
        "name": "Performance Optimization",
        "score": 80
      }
    ],
    "points_earned": 85,
    "focus_questions": [
      "Improve microservices knowledge",
      "Practice system design patterns"
    ],
    "summary_feedback": "Strong technical skills with room for improvement in system design."
  },
  "updated_at": "2025-01-15T11:15:00.000Z"
}
```

**Error Responses**:
```json
// 404 Not Found
{
  "detail": "Interview not found or user doesn't have access"
}

// 400 Bad Request
{
  "detail": "Invalid user ID or interview ID format"
}
```

---

## 🔄 Common Response Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid parameters or business rule violation |
| 401 | Unauthorized | Invalid or missing Bearer token |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error in request format |
| 500 | Internal Server Error | Server error |

---

## 🧪 Testing with cURL

### 1. Generate Questions
```bash
curl -X POST "https://teching.tech/interviewready/api/v1/interview/questions/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "507f1f77bcf86cd799439011",
    "user_seniority": "senior",
    "user_specialization": "backend",
    "type": "technical",
    "question_number": {"value": 10}
  }'
```

### 2. Submit Answer
```bash
curl -X POST "https://teching.tech/interviewready/api/v1/interview/questions/response/INTERVIEW_ID?user_response=My%20answer&user_id=USER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get Feedback
```bash
curl -X GET "https://teching.tech/interviewready/api/v1/interview/questions/feedback/INTERVIEW_ID?user_id=USER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get History
```bash
curl -X GET "https://teching.tech/interviewready/api/v1/interview/history/USER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Interview Details
```bash
curl -X GET "https://teching.tech/interviewready/api/v1/interview/history/USER_ID/INTERVIEW_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Business Rules Summary

### Input Validation
- **User Seniority**: `["junior", "mid", "senior", "lead", "principal"]` (case-insensitive)
- **Interview Type**: `["behavioral", "structured", "technical", "simulation"]` (case-insensitive)
- **Question Count**: `[5, 10, 15, 30]` (exact values only)
- **User ID**: MongoDB ObjectId format (24 hex characters)
- **Specialization**: Free text, 1-100 characters

### Interview Flow
1. **Create Interview** → Generates questions and starts with first question
2. **Submit Answers** → AI evaluates quality and advances or repeats question
3. **Complete Interview** → All questions answered, status becomes "completed"
4. **Get Feedback** → Comprehensive AI analysis with scores and recommendations

### Data Security
- All text inputs are sanitized for XSS prevention
- Bearer token authentication required for all endpoints
- Input length validation and content filtering applied

---

## 🚀 Rate Limits & Performance

- **Rate Limit**: Not specified (implement client-side throttling)
- **Timeout**: Recommend 30-60 seconds for question generation
- **Retry Strategy**: Exponential backoff for 5xx errors
- **Caching**: Cache interview details to reduce API calls

---

This documentation provides complete endpoint specifications for integrating with the Interview Ready API at `https://teching.tech/interviewready/api/v1`.
