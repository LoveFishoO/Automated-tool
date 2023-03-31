import json
import requests

import datetime
import smtplib

from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatad

sender_mail = 'xxxxxxxx'
sender_pass = 'xxxxxxxx'

receive_mail = 'xxxxxxx'

def get_date():
    date = datetime.date.today()
    year = date.year
    month = date.month
    day = date.day
    return f'{year}-{month}-{day}'
  

def mail_login():
    
    server = smtplib.SMTP_SSL("smtp.163.com", 587)  
    server.login(sender_mail, sender_pass)  

    return server
    

def send_mail(subject, content):
    date = get_date()
    
    server = mail_login()
    
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = formataddr([f"Leetcode 每日一题 {date}", sender_mail])
    msg['To'] = formataddr(["LoveFishO", receive_mail])
    msg['Subject'] = subject

    server.sendmail(sender_mail, [receive_mail,], msg.as_string())
    server.quit()
    
 def update_csrf(url):
    session.get(url)
    return None


def get_today_question(url, headers):
    param = '''
    query questionOfToday {
      todayRecord {
        date
        userStatus
        question {
          questionId
          frontendQuestionId: questionFrontendId
          difficulty
          title
          titleCn: translatedTitle
          titleSlug
          paidOnly: isPaidOnly
          freqBar
          isFavor
          acRate
          status
          solutionNum
          hasVideoSolution
          topicTags {
            name
            nameTranslated: translatedName
            id
          }
          extra {
            topCompanyTags {
              imgUrl
              slug
              numSubscribed
            }
          }
        }
        lastSubmission {
          id
        }
      }
    }
    '''

    data = {
        "query": param,
        "variables": {}
    }

    response = session.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def get_question_data(url, headers, title_slug):
    param = '''
    query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            categoryTitle
            boundTopicId
            title
            titleSlug
            content
            translatedTitle
            translatedContent
            isPaidOnly
            difficulty
            likes
            dislikes
            isLiked
            similarQuestions
            contributors {
              username
              profileUrl
              avatarUrl
              __typename
            }
            langToValidPlayground
            topicTags {
              name
              slug
              translatedName
              __typename
            }
            companyTagStats
            codeSnippets {
              lang
              langSlug
              code
              __typename
            }
            stats
            hints
            solution {
              id
              canSeeDetail
              __typename
            }
            status
            sampleTestCase
            metaData
            judgerAvailable
            judgeType
            mysqlSchemas
            enableRunCode
            envInfo
            book {
              id
              bookName
              pressName
              source
              shortDescription
              fullDescription
              bookImgUrl
              pressImgUrl
              productUrl
              __typename
            }
            isSubscribed
            isDailyQuestion
            dailyRecordStatus
            editorType
            ugcQuestionId
            style
            exampleTestcases
            jsonExampleTestcases
            __typename
          }
        }
    '''
    data = {
        "operationName": "questionData",
        "variables": {
            "titleSlug": title_slug
        },
        "query": param
    }
    response = session.post(url, headers=headers, data=json.dumps(data))
    return response.json()


if __name__ == '__main__':
    session = requests.session()

    base_url = 'https://leetcode.cn'
    graphql_url = '/graphql'
    url = base_url + graphql_url

    update_csrf(url=url)
    
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    headers = {
        'x-requested-with': 'XMLHttpRequest',
        'accept': '*/*',
        'user-agent': user_agent,
        'connection': 'keep-alive',
        'origin': 'https://leetcode.cn',
        'content-type': 'application/json',
        'x-csrftoken': session.cookies['csrftoken'],
        # 'cookies':'cookies'
    }

    tq = get_today_question(url=url, headers=headers)
    title_slug = tq['data']['todayRecord'][0]['question']['titleSlug']
    
    qd = get_question_data(url=url, headers=headers, title_slug=title_slug)
    
    question_info = qd['data']['question']
    question_id = question_info['questionFrontendId']
    question_content = question_info['translatedContent']
    question_difficulty = question_info['difficulty']
    
    similar_questions = question_info['similarQuestions']
    
    stats = eval(question_info['stats'])
    
    acrate = stats['acRate']
    total_accepted = stats['totalAccepted']
    total_submission = stats['totalSubmission']
    
    question_url = 'https://leetcode.cn/problems/' + title_slug
    
    tags = []
    for i in question_info['topicTags']:
        tags.append(i['translatedName'])
    tags_str = ' '.join(tags)
    
    mail_content = """题目名称：%s.%s&nbsp&nbsp&nbsp&nbsp&nbsp题目难度：<strong>%s</strong>&nbsp&nbsp&nbsp&nbsp&nbspAC率：%s&nbsp&nbsp&nbsp&nbsp&nbsp题目链接：<a href="%s">%s</a><br>题目标签：%s<br>%s""" % (question_id, question_title, question_difficulty, acrate, question_url, question_url, tags_str, question_content)
    mail_content.strip()

    date = get_date_md()
    subject = f'力扣{date}每日一题来咯！！！（{question_id}.{question_title}）'
    send_mail(subject=subject, content=mail_content,
              fromid=f"Leetcode 每日一题 {date}")
    
    
