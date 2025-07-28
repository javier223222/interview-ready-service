# 📱 Interview Ready Microservice - Flutter Integration Guide

## 🔗 API Base Information

**Base URL**: `https://teching.tech/interviewready/api/v1`

**Authentication**: All endpoints require Bearer token authentication
```
Authorization: Bearer <your_access_token>
```

**Content-Type**: `application/json`

---

## 📋 API Endpoints Documentation

### 1. 🚀 Generate Interview Questions

**Endpoint**: `POST /interview/questions/generate`

**Description**: Generates a set of interview questions based on user profile

**Request Body**:
```dart
class QuestionCount {
  final int value;              // Number of questions (5, 10, 15, or 30)

  QuestionCount({required this.value});

  Map<String, dynamic> toJson() => {'value': value};

  factory QuestionCount.fromJson(Map<String, dynamic> json) => QuestionCount(
    value: json['value'],
  );
}

class CreateInterviewRequest {
  final String userId;           // Required: User identifier
  final String userSeniority;    // Required: User seniority level
  final String userSpecialization; // Required: User's technical area
  final String type;             // Required: Interview type
  final QuestionCount questionNumber; // Required: Question count object

  CreateInterviewRequest({
    required this.userId,
    required this.userSeniority,
    required this.userSpecialization,
    required this.type,
    required this.questionNumber,
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'user_seniority': userSeniority,
    'user_specialization': userSpecialization,
    'type': type,
    'question_number': questionNumber.toJson(),
  };
}
```

**Example JSON Request**:
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

**Business Rules**:
- `userSeniority`: Must be one of: `['junior', 'mid', 'senior', 'lead', 'principal']`
- `type`: Must be one of: `['behavioral', 'structured', 'technical', 'simulation']`
- `questionNumber.value`: Must be one of: `[5, 10, 15, 30]`
- `userId`: Required MongoDB ObjectId format string
- `userSpecialization`: Required string (e.g., "backend", "frontend", "fullstack", "mobile", etc.)

**Response** (201 Created):
```dart
class InterviewResponse {
  final String id;                    // Interview session ID
  final String userId;                // User ID
  final String type;                  // Interview type
  final Question currentQuestion;     // Current question object
  final Question? nextQuestion;       // Next question (null if last)
  final String initAt;               // ISO timestamp of interview start
  final String status;               // Interview status
  final int questionNumber;          // Total number of questions
  final int actualQuestion;          // Current question ID
  final String? feedback;            // Feedback for current question
  final String? message;             // Additional message

  InterviewResponse({
    required this.id,
    required this.userId,
    required this.type,
    required this.currentQuestion,
    this.nextQuestion,
    required this.initAt,
    required this.status,
    required this.questionNumber,
    required this.actualQuestion,
    this.feedback,
    this.message,
  });

  factory InterviewResponse.fromJson(Map<String, dynamic> json) => InterviewResponse(
    id: json['id'],
    userId: json['user_id'],
    type: json['type'],
    currentQuestion: Question.fromJson(json['current_question']),
    nextQuestion: json['next_question'] != null ? Question.fromJson(json['next_question']) : null,
    initAt: json['init_at'],
    status: json['status'],
    questionNumber: json['question_number'],
    actualQuestion: json['actual_question'],
    feedback: json['feedback'],
    message: json['message'],
  );
}

class Question {
  final int id;                      // Question identifier
  final String question;             // Question text
  final String? answer;              // User's answer (if any)
  final String? feedback;            // AI feedback (if any)
  final String competency;           // Competency being evaluated
  final String difficulty;           // Question difficulty level

  Question({
    required this.id,
    required this.question,
    this.answer,
    this.feedback,
    required this.competency,
    required this.difficulty,
  });

  factory Question.fromJson(Map<String, dynamic> json) => Question(
    id: json['id'],
    question: json['question'],
    answer: json['answer'],
    feedback: json['feedback'],
    competency: json['competency'],
    difficulty: json['difficulty'],
  );
}
```

**Error Responses**:
- `400`: Invalid input parameters or business rule violation
- `422`: Validation error in request format
- `500`: Internal server error

---

### 2. 💬 Submit Answer to Question

**Endpoint**: `POST /interview/questions/response/{interview_id}`

**Description**: Submits user's answer to current question and advances to next question

**Path Parameters**:
- `interview_id` (string): The interview session ID

**Query Parameters**:
- `user_response` (string): The user's answer to the current question
- `user_id` (string): The user identifier

**Example Request**:
```dart
// URL: https://teching.tech/interviewready/api/v1/interview/questions/response/60f7b3b3b3b3b3b3b3b3b3b3?user_response=My answer to the question&user_id=507f1f77bcf86cd799439011

Future<InterviewResponse> submitAnswer(String interviewId, String userResponse, String userId) async {
  final uri = Uri.parse('$baseUrl/interview/questions/response/$interviewId').replace(
    queryParameters: {
      'user_response': userResponse,
      'user_id': userId,
    },
  );
  
  final response = await http.post(
    uri,
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    return InterviewResponse.fromJson(json.decode(response.body));
  } else {
    throw Exception('Failed to submit answer: ${response.body}');
  }
}
```

**Response** (200 OK):
Same structure as `InterviewResponse` above, but with updated question progression.

**Business Rules**:
- User response will be evaluated by AI for quality
- If response quality is good, advances to next question
- If response quality is poor, stays on same question
- When all questions are answered, interview status becomes "completed"
- Response is automatically sanitized for security

**Error Responses**:
- `400`: Invalid interview ID or user ID
- `404`: Interview not found
- `422`: Validation error in parameters
- `500`: Internal server error

---

### 3. 📊 Get Interview Feedback

**Endpoint**: `GET /interview/questions/feedback/{interview_id}`

**Description**: Retrieves comprehensive feedback after interview completion

**Path Parameters**:
- `interview_id` (string): The interview session ID

**Query Parameters**:
- `user_id` (string): The user identifier

**Response** (200 OK):
```dart
class InterviewFeedback {
  final String interviewId;          // Interview session ID
  final String userId;               // User ID
  final int pointsEarned;            // Total points earned
  final FeedbackDetail feedback;     // Detailed feedback object
  final String initAt;               // Interview start time
  final String finishAt;             // Interview completion time

  InterviewFeedback({
    required this.interviewId,
    required this.userId,
    required this.pointsEarned,
    required this.feedback,
    required this.initAt,
    required this.finishAt,
  });

  factory InterviewFeedback.fromJson(Map<String, dynamic> json) => InterviewFeedback(
    interviewId: json['interview_id'],
    userId: json['user_id'],
    pointsEarned: json['points_earned'],
    feedback: FeedbackDetail.fromJson(json['feedback']),
    initAt: json['init_at'],
    finishAt: json['finish_at'],
  );
}

class FeedbackDetail {
  final int overallScore;                        // Overall interview score (0-100)
  final List<CompetencyBreakdown> competencyBreakdown; // Score breakdown by competency
  final int pointsEarned;                        // Points earned (0-100)
  final List<String> focusQuestions;             // Areas for improvement
  final String summaryFeedback;                  // AI-generated summary

  FeedbackDetail({
    required this.overallScore,
    required this.competencyBreakdown,
    required this.pointsEarned,
    required this.focusQuestions,
    required this.summaryFeedback,
  });

  factory FeedbackDetail.fromJson(Map<String, dynamic> json) => FeedbackDetail(
    overallScore: json['overall_score'],
    competencyBreakdown: (json['competency_breakdown'] as List)
        .map((item) => CompetencyBreakdown.fromJson(item))
        .toList(),
    pointsEarned: json['points_earned'],
    focusQuestions: List<String>.from(json['focus_questions']),
    summaryFeedback: json['summary_feedback'],
  );
}

class CompetencyBreakdown {
  final String name;                 // Competency name
  final int score;                   // Score for this competency (0-100)

  CompetencyBreakdown({
    required this.name,
    required this.score,
  });

  factory CompetencyBreakdown.fromJson(Map<String, dynamic> json) => CompetencyBreakdown(
    name: json['name'],
    score: json['score'],
  );
}
```

**Business Rules**:
- Only available after interview is completed (status: "completed")
- Feedback is generated by AI based on all answers provided
- Scores range from 0-100
- Competency breakdown shows performance in different areas

**Error Responses**:
- `400`: Invalid interview ID or interview not completed
- `404`: Interview not found
- `500`: Internal server error

---

### 4. 📜 Get User Interview History

**Endpoint**: `GET /interview/history/{user_id}`

**Description**: Retrieves all interviews conducted by a specific user

**Path Parameters**:
- `user_id` (string): The user identifier

**Response** (200 OK):
```dart
class InterviewHistory {
  final List<InterviewSummary> interviews; // List of user's interviews
  final int total;                         // Total number of interviews

  InterviewHistory({
    required this.interviews,
    required this.total,
  });

  factory InterviewHistory.fromJson(Map<String, dynamic> json) => InterviewHistory(
    interviews: (json['interviews'] as List)
        .map((item) => InterviewSummary.fromJson(item))
        .toList(),
    total: json['total'],
  );
}

class InterviewSummary {
  final String userId;                     // User ID
  final String userSeniority;              // User seniority at time of interview
  final String type;                       // Interview type
  final String userSpecialization;         // User specialization
  final String initAt;                     // Interview start time
  final String endAt;                      // Interview end time
  final String status;                     // Interview status
  final int questionsNumber;               // Number of questions in interview
  final int pointsEarned;                  // Points earned
  final String updatedAt;                  // Last update timestamp
  final String id;                         // Interview ID

  InterviewSummary({
    required this.userId,
    required this.userSeniority,
    required this.type,
    required this.userSpecialization,
    required this.initAt,
    required this.endAt,
    required this.status,
    required this.questionsNumber,
    required this.pointsEarned,
    required this.updatedAt,
    required this.id,
  });

  factory InterviewSummary.fromJson(Map<String, dynamic> json) => InterviewSummary(
    userId: json['user_id'],
    userSeniority: json['user_seniority'],
    type: json['type'],
    userSpecialization: json['user_specialization'],
    initAt: json['init_at'],
    endAt: json['end_at'],
    status: json['status'],
    questionsNumber: json['questions_number'],
    pointsEarned: json['points_earned'],
    updatedAt: json['updated_at'],
    id: json['id'],
  );
}
```

**Business Rules**:
- Returns all interviews for the specified user
- Interviews are ordered by creation date (most recent first)
- Includes both completed and in-progress interviews

**Error Responses**:
- `404`: No interviews found for user
- `400`: Invalid user ID format
- `500`: Internal server error

---

### 5. 🔍 Get Specific Interview Details

**Endpoint**: `GET /interview/history/{user_id}/{interview_id}`

**Description**: Retrieves complete details of a specific interview

**Path Parameters**:
- `user_id` (string): The user identifier
- `interview_id` (string): The interview session ID

**Response** (200 OK):
```dart
class InterviewDetails {
  final String userId;                     // User ID
  final String type;                       // Interview type
  final String userSeniority;              // User seniority
  final String userSpecialization;         // User specialization
  final List<Question> questions;          // All questions with answers
  final String initAt;                     // Interview start time
  final String? endAt;                     // Interview end time (null if in progress)
  final String status;                     // Interview status
  final int questionNumber;                // Total questions
  final Question? actualQuestion;          // Current question (if in progress)
  final Question? previousQuestion;        // Previous question
  final int pointsEarned;                  // Points earned
  final FeedbackDetail? feedback;          // Feedback (if completed)
  final String? updatedAt;                 // Last update

  InterviewDetails({
    required this.userId,
    required this.type,
    required this.userSeniority,
    required this.userSpecialization,
    required this.questions,
    required this.initAt,
    this.endAt,
    required this.status,
    required this.questionNumber,
    this.actualQuestion,
    this.previousQuestion,
    required this.pointsEarned,
    this.feedback,
    this.updatedAt,
  });

  factory InterviewDetails.fromJson(Map<String, dynamic> json) => InterviewDetails(
    userId: json['userId'],
    type: json['type'],
    userSeniority: json['user_seniority'],
    userSpecialization: json['user_specialization'],
    questions: (json['questions'] as List)
        .map((item) => Question.fromJson(item))
        .toList(),
    initAt: json['init_at'],
    endAt: json['end_at'],
    status: json['status'],
    questionNumber: json['question_number'],
    actualQuestion: json['actual_question'] != null 
        ? Question.fromJson(json['actual_question']) 
        : null,
    previousQuestion: json['previus_question'] != null 
        ? Question.fromJson(json['previus_question']) 
        : null,
    pointsEarned: json['points_earned'],
    feedback: json['feedback'] != null 
        ? FeedbackDetail.fromJson(json['feedback']) 
        : null,
    updatedAt: json['updated_at'],
  );
}
```

**Business Rules**:
- Returns complete interview data including all questions and answers
- Can be used to resume in-progress interviews
- Shows progression through questions and current state

**Error Responses**:
- `404`: Interview not found or user doesn't have access
- `400`: Invalid user ID or interview ID format
- `500`: Internal server error

---

## 🔐 Authentication Implementation

### Setup HTTP Client with Authentication

```dart
class InterviewApiClient {
  final String baseUrl = 'https://teching.tech/interviewready/api/v1';
  final String? accessToken;

  InterviewApiClient({this.accessToken});

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (accessToken != null) 'Authorization': 'Bearer $accessToken',
  };

  Future<http.Response> get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  Future<http.Response> post(String endpoint, {Map<String, dynamic>? body}) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
      body: body != null ? json.encode(body) : null,
    );
    return _handleResponse(response);
  }

  http.Response _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response;
    } else {
      throw ApiException(
        statusCode: response.statusCode,
        message: _extractErrorMessage(response.body),
      );
    }
  }

  String _extractErrorMessage(String responseBody) {
    try {
      final json = jsonDecode(responseBody);
      return json['detail'] ?? 'Unknown error occurred';
    } catch (e) {
      return responseBody;
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
```

---

## 🏗️ Business Rules & Validation

### 1. Input Validation Rules

**User Seniority**:
- Allowed values: `['junior', 'mid', 'senior', 'lead', 'principal']`
- Case-insensitive, will be converted to lowercase
- Required field

**Interview Type**:
- Allowed values: `['behavioral', 'structured', 'technical', 'simulation']`
- Case-insensitive, will be converted to lowercase
- Required field

**Question Count**:
- Allowed values: `[5, 10, 15, 30]`
- Must be exact match
- Required field

**User Specialization**:
- Free text field but should represent technical areas
- Common values: "backend", "frontend", "fullstack", "mobile", "devops", "data", etc.
- Required field, min 1 character, max 100 characters

**User ID**:
- Must be valid MongoDB ObjectId format (24 character hex string)
- Required field

### 2. Interview Flow Rules

**Question Progression**:
1. Interview starts with first question
2. User submits answer
3. AI evaluates answer quality
4. If good quality → advance to next question
5. If poor quality → stay on same question
6. When all questions answered → interview status becomes "completed"

**Interview States**:
- `"in_progress"`: Interview is active, user can submit answers
- `"completed"`: All questions answered, feedback available

**Response Quality Evaluation**:
- AI analyzes response completeness, relevance, and depth
- Poor responses require re-answering the same question
- Quality threshold is determined by AI evaluation

### 3. Data Constraints

**Text Fields**:
- All text inputs are sanitized for security
- HTML tags and scripts are removed
- Maximum length varies by field (typically 500-2000 characters)
- Minimum meaningful length enforced (typically 10 characters for responses)

**Timestamps**:
- All timestamps are in ISO 8601 format with UTC timezone
- Example: "2025-01-15T10:30:00.000Z"

**Scores and Points**:
- Range: 0-100
- Integer values only
- Based on AI evaluation of responses

---

## 💡 Integration Examples

### Complete Interview Flow Example

```dart
class InterviewService {
  final InterviewApiClient _client;
  
  InterviewService(String accessToken) : _client = InterviewApiClient(accessToken: accessToken);

  // 1. Start new interview
  Future<InterviewResponse> startInterview({
    required String userId,
    required String seniority,
    required String specialization,
    required String type,
    required int questionCount,
  }) async {
    final request = CreateInterviewRequest(
      userId: userId,
      userSeniority: seniority,
      userSpecialization: specialization,
      type: type,
      questionNumber: QuestionCount(value: questionCount),
    );

    final response = await _client.post(
      '/interview/questions/generate',
      body: request.toJson(),
    );

    return InterviewResponse.fromJson(json.decode(response.body));
  }

  // 2. Submit answer and get next question
  Future<InterviewResponse> submitAnswer({
    required String interviewId,
    required String userId,
    required String answer,
  }) async {
    final uri = Uri.parse('/interview/questions/response/$interviewId').replace(
      queryParameters: {
        'user_response': answer,
        'user_id': userId,
      },
    );

    final response = await _client.post(uri.toString());
    return InterviewResponse.fromJson(json.decode(response.body));
  }

  // 3. Get final feedback
  Future<InterviewFeedback> getFeedback({
    required String interviewId,
    required String userId,
  }) async {
    final response = await _client.get(
      '/interview/questions/feedback/$interviewId?user_id=$userId'
    );

    return InterviewFeedback.fromJson(json.decode(response.body));
  }

  // 4. Get user history
  Future<InterviewHistory> getUserHistory(String userId) async {
    final response = await _client.get('/interview/history/$userId');
    return InterviewHistory.fromJson(json.decode(response.body));
  }

  // 5. Resume interview or get details
  Future<InterviewDetails> getInterviewDetails({
    required String userId,
    required String interviewId,
  }) async {
    final response = await _client.get('/interview/history/$userId/$interviewId');
    return InterviewDetails.fromJson(json.decode(response.body));
  }
}
```

### Error Handling Example

```dart
class InterviewManager {
  final InterviewService _service;
  
  InterviewManager(this._service);

  Future<InterviewResponse?> startInterviewSafe({
    required String userId,
    required String seniority,
    required String specialization,
    required String type,
    required int questionCount,
  }) async {
    try {
      return await _service.startInterview(
        userId: userId,
        seniority: seniority,
        specialization: specialization,
        type: type,
        questionCount: questionCount,
      );
    } on ApiException catch (e) {
      switch (e.statusCode) {
        case 400:
          throw InterviewException('Invalid parameters: ${e.message}');
        case 422:
          throw InterviewException('Validation error: ${e.message}');
        case 500:
          throw InterviewException('Server error. Please try again later.');
        default:
          throw InterviewException('Unexpected error: ${e.message}');
      }
    } catch (e) {
      throw InterviewException('Network error: Please check your connection.');
    }
  }
}

class InterviewException implements Exception {
  final String message;
  InterviewException(this.message);
  
  @override
  String toString() => message;
}
```

---

## 🔧 Configuration & Environment

### Required Dependencies

Add to your `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
  json_annotation: ^4.8.1

dev_dependencies:
  json_serializable: ^6.7.1
  build_runner: ^2.4.7
```

### Environment Configuration

```dart
class Config {
  static const String baseUrl = 'https://teching.tech/interviewready/api/v1';
  
  // Validation constants
  static const List<String> allowedSeniorities = [
    'junior', 'mid', 'senior', 'lead', 'principal'
  ];
  
  static const List<String> allowedInterviewTypes = [
    'behavioral', 'structured', 'technical', 'simulation'
  ];
  
  static const List<int> allowedQuestionCounts = [5, 10, 15, 30];
  
  // Common specializations (for UI suggestions)
  static const List<String> commonSpecializations = [
    'backend', 'frontend', 'fullstack', 'mobile', 'devops', 
    'data', 'ai/ml', 'security', 'qa', 'architecture'
  ];
}
```

---

## 🚨 Important Notes

### Security Considerations
1. **Always use HTTPS** - The API is only available over HTTPS
2. **Store tokens securely** - Use secure storage for access tokens
3. **Validate inputs** - Client-side validation should match server rules
4. **Handle sensitive data** - Interview responses may contain personal information

### Performance Tips
1. **Cache interview details** - Avoid repeated API calls for same interview
2. **Implement retry logic** - Handle temporary network failures
3. **Use pagination** - For users with many interviews, implement pagination
4. **Optimize payloads** - Only request data you need

### Best Practices
1. **Graceful error handling** - Provide meaningful error messages to users
2. **Loading states** - Show progress during API calls
3. **Offline support** - Cache critical data for offline access
4. **User experience** - Auto-save responses to prevent data loss

---

## 📞 Support & Troubleshooting

### Common Error Scenarios

| Status Code | Common Cause | Solution |
|-------------|--------------|----------|
| 401 | Invalid or expired token | Refresh authentication token |
| 400 | Invalid parameters | Check parameter values against business rules |
| 422 | Validation error | Ensure request format matches expected schema |
| 404 | Resource not found | Verify IDs and user permissions |
| 500 | Server error | Implement retry logic with exponential backoff |

### Testing Checklist

- [ ] Authentication with valid token
- [ ] All endpoint responses parse correctly
- [ ] Error handling for all status codes
- [ ] Input validation matches server rules
- [ ] Complete interview flow works end-to-end
- [ ] Edge cases (empty responses, invalid IDs)
- [ ] Network failure scenarios
- [ ] Token expiration handling

---

This documentation provides everything needed to integrate the Interview Ready microservice into your Flutter application. All endpoints, data models, business rules, and error scenarios are covered based on the actual implementation.
