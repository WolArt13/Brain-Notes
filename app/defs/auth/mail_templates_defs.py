def get_verification_email_html(username: str, verification_link: str) -> str:
    """
    HTML шаблон для письма подтверждения email.
    Стилизован в едином стиле Brain Notes с более контрастными цветами.
    """
    return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Подтверждение Email - Brain Notes</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #1a1a2e;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #ffffff;
            font-weight: 700;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #1a1a2e;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 30px;
        }}
        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}
        .verify-button {{
            display: inline-block;
            padding: 16px 40px;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            color: #ffffff;
            text-decoration: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
        }}
        .link-section {{
            margin-top: 30px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }}
        .link-label {{
            font-size: 14px;
            color: #64748b;
            margin-bottom: 10px;
        }}
        .link-text {{
            font-size: 14px;
            color: #00d9ff;
            word-break: break-all;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
            border-top: 1px solid #e2e8f0;
            background: #f7fafc;
        }}
        .footer-logo {{
            font-size: 18px;
            font-weight: 600;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Brain Notes</h1>
        </div>

        <div class="content">
            <div class="greeting">Здравствуйте, {username}!</div>

            <div class="message">
                Спасибо за регистрацию в <strong>Brain Notes</strong> — вашем персональном пространстве для организации мыслей и идей в виде связанного дерева заметок.
            </div>

            <div class="message">
                Для завершения регистрации, пожалуйста, подтвердите ваш email адрес, нажав на кнопку ниже:
            </div>

            <div class="button-container">
                <a href="{verification_link}" class="verify-button">Подтвердить Email</a>
            </div>

            <div class="link-section">
                <div class="link-label">Или скопируйте и вставьте ссылку в браузер:</div>
                <div class="link-text">{verification_link}</div>
            </div>

            <div class="message" style="margin-top: 30px; font-size: 14px; color: #64748b;">
                Если вы не регистрировались в Brain Notes, просто проигнорируйте это письмо.
            </div>
        </div>

        <div class="footer">
            <div class="footer-logo">Brain Notes</div>
            <div>Организуйте свои мысли. Создавайте связи. Развивайтесь.</div>
        </div>
    </div>
</body>
</html>
'''

def get_change_email_html(username: str, verification_link: str, new_email: str, expire_hours: int) -> str:
    """
    HTML шаблон для письма подтверждения смены email.
    Совместимо со всеми почтовыми клиентами (table-based layout).
    """
    return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Подтверждение смены email - Brain Notes</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <!-- Основной контейнер -->
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 20px; overflow: hidden; max-width: 600px;">
                    
                    <!-- Хедер -->
                    <tr>
                        <td style="background-color: #4facfe; padding: 50px 30px; text-align: center;">
                            <div style="font-size: 48px; margin-bottom: 15px;">📧</div>
                            <h1 style="margin: 0; font-size: 36px; color: #ffffff; font-weight: 700;">Brain Notes</h1>
                            <div style="margin: 10px 0 0 0; font-size: 14px; color: rgba(255, 255, 255, 0.95);">Подтверждение смены email</div>
                        </td>
                    </tr>
                    
                    <!-- Контент -->
                    <tr>
                        <td style="padding: 50px 40px;">
                            
                            <div style="font-size: 24px; margin-bottom: 25px; color: #1a1a2e; font-weight: 600;">
                                Здравствуйте, {username}! 👋
                            </div>
                            
                            <p style="font-size: 16px; line-height: 1.8; color: #4a5568; margin-bottom: 25px;">
                                Вы запросили смену email адреса для вашей учётной записи в <strong>Brain Notes</strong>.
                            </p>
                            
                            <!-- Highlight box -->
                            <table width="100%" cellpadding="20" cellspacing="0" border="0" style="background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px; margin: 30px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <div style="font-size: 14px; color: #0369a1; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                                            Новый email адрес
                                        </div>
                                        <div style="font-size: 20px; color: #0284c7; font-weight: 600; word-break: break-all;">
                                            {new_email}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="font-size: 16px; line-height: 1.8; color: #4a5568; margin-bottom: 25px;">
                                Чтобы завершить процесс смены email, нажмите на кнопку ниже. После подтверждения вы сможете использовать новый email для входа в систему.
                            </p>
                            
                            <!-- Кнопка -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 45px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{verification_link}" style="display: inline-block; padding: 18px 50px; background-color: #4facfe; color: #ffffff; text-decoration: none; border-radius: 12px; font-size: 18px; font-weight: 600;">
                                            ✅ Подтвердить смену email
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Expire notice -->
                            <table width="100%" cellpadding="15" cellspacing="0" border="0" style="background-color: #f8fafc; border-radius: 8px; margin-top: 25px;">
                                <tr>
                                    <td style="text-align: center; font-size: 15px; color: #64748b;">
                                        ⏱️ Ссылка действительна в течение <strong style="color: #0284c7;">{expire_hours} часов</strong>
                                    </td>
                                </tr>
                            </table>
                            
                            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                            
                            <!-- Info box -->
                            <table width="100%" cellpadding="20" cellspacing="0" border="0" style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; margin: 30px 0;">
                                <tr>
                                    <td>
                                        <div style="font-size: 14px; color: #1e40af; margin-bottom: 10px; font-weight: 600;">
                                            💡 Что произойдёт после подтверждения?
                                        </div>
                                        <div style="font-size: 14px; color: #475569; line-height: 1.6;">
                                            • Ваш текущий email будет заменён на новый<br>
                                            • Для входа нужно будет использовать новый email<br>
                                            • Все ваши заметки и данные останутся без изменений
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Ссылка для копирования -->
                            <table width="100%" cellpadding="20" cellspacing="0" border="0" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin: 30px 0;">
                                <tr>
                                    <td>
                                        <div style="font-size: 13px; color: #94a3b8; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                                            Или скопируйте ссылку в браузер
                                        </div>
                                        <div style="font-size: 13px; color: #0284c7; word-break: break-all; line-height: 1.6;">
                                            {verification_link}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Warning box -->
                            <table width="100%" cellpadding="20" cellspacing="0" border="0" style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; margin: 30px 0;">
                                <tr>
                                    <td>
                                        <div style="font-size: 16px; font-weight: 600; color: #dc2626; margin-bottom: 12px;">
                                            ⚠️ Важная информация
                                        </div>
                                        <div style="font-size: 14px; color: #7f1d1d; line-height: 1.6;">
                                            Если вы <strong>не запрашивали</strong> смену email адреса, просто проигнорируйте это письмо. 
                                            Ваш текущий email останется без изменений, и никто не получит доступ к вашей учётной записи.
                                            <br><br>
                                            <strong>Никогда не сообщайте эту ссылку другим людям!</strong>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- Футер -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center; background-color: #f8fafc; border-top: 1px solid #e2e8f0;">
                            <div style="font-size: 24px; font-weight: 700; color: #4facfe; margin-bottom: 15px;">
                                Brain Notes
                            </div>
                            <div style="color: #64748b; margin-bottom: 20px; font-style: italic;">
                                Организуйте свои мысли • Создавайте связи • Развивайтесь
                            </div>
                            <div style="color: #94a3b8; font-size: 12px;">
                                © 2025 Brain Notes. Все права защищены.
                            </div>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''


def get_password_reset_email_html(username: str, reset_link: str, expire_hours: int) -> str:
    """
    HTML шаблон для письма сброса пароля.
    Стилизован в едином стиле Brain Notes с контрастными цветами.
    """
    return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сброс пароля - Brain Notes</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #1a1a2e;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #ffffff;
            font-weight: 700;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #1a1a2e;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 30px;
        }}
        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}
        .reset-button {{
            display: inline-block;
            padding: 16px 40px;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            color: #ffffff;
            text-decoration: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
        }}
        .warning-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }}
        .warning-title {{
            font-size: 16px;
            font-weight: 600;
            color: #dc2626;
            margin-bottom: 10px;
        }}
        .warning-text {{
            font-size: 14px;
            color: #7f1d1d;
        }}
        .link-section {{
            margin-top: 30px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }}
        .link-label {{
            font-size: 14px;
            color: #64748b;
            margin-bottom: 10px;
        }}
        .link-text {{
            font-size: 14px;
            color: #00d9ff;
            word-break: break-all;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
            border-top: 1px solid #e2e8f0;
            background: #f7fafc;
        }}
        .footer-logo {{
            font-size: 18px;
            font-weight: 600;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .expire-notice {{
            text-align: center;
            font-size: 14px;
            color: #64748b;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Brain Notes</h1>
        </div>

        <div class="content">
            <div class="greeting">Здравствуйте, {username}!</div>

            <div class="message">
                Вы запросили сброс пароля для вашей учётной записи в <strong>Brain Notes</strong>.
            </div>

            <div class="message">
                Для создания нового пароля нажмите на кнопку ниже:
            </div>

            <div class="button-container">
                <a href="{reset_link}" class="reset-button">Сбросить пароль</a>
            </div>

            <div class="expire-notice">
                ⏱️ Ссылка действительна <strong>{expire_hours} часов</strong>
            </div>

            <div class="link-section">
                <div class="link-label">Или скопируйте и вставьте ссылку в браузер:</div>
                <div class="link-text">{reset_link}</div>
            </div>

            <div class="warning-box">
                <div class="warning-title">⚠️ Важная информация</div>
                <div class="warning-text">
                    Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо. 
                    Ваш пароль останется без изменений. Никому не сообщайте эту ссылку.
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="footer-logo">Brain Notes</div>
            <div>Организуйте свои мысли. Создавайте связи. Развивайтесь.</div>
        </div>
    </div>
</body>
</html>
'''


def get_welcome_email_html(username: str, dashboard_url: str = "https://brainnotes.com/dashboard") -> str:
    """
    HTML шаблон приветственного письма после успешной верификации.
    Стилизован в едином стиле Brain Notes с контрастными цветами.
    """
    return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Добро пожаловать - Brain Notes</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #1a1a2e;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #ffffff;
            font-weight: 700;
        }}
        .header .emoji {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #1a1a2e;
            text-align: center;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 20px;
        }}
        .features {{
            margin: 30px 0;
        }}
        .feature-item {{
            display: flex;
            align-items: start;
            margin-bottom: 20px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }}
        .feature-icon {{
            font-size: 24px;
            margin-right: 15px;
        }}
        .feature-text {{
            flex: 1;
        }}
        .feature-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 5px;
        }}
        .feature-description {{
            font-size: 14px;
            color: #64748b;
        }}
        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}
        .start-button {{
            display: inline-block;
            padding: 16px 40px;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            color: #ffffff;
            text-decoration: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
            border-top: 1px solid #e2e8f0;
            background: #f7fafc;
        }}
        .footer-logo {{
            font-size: 18px;
            font-weight: 600;
            background: linear-gradient(135deg, #00d9ff, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="emoji">🎉</div>
            <h1>Добро пожаловать!</h1>
        </div>

        <div class="content">
            <div class="greeting">Привет, {username}!</div>

            <div class="message">
                Ваш email успешно подтверждён! Теперь вы можете в полной мере использовать все возможности <strong>Brain Notes</strong>.
            </div>

            <div class="features">
                <div class="feature-item">
                    <div class="feature-icon">🌳</div>
                    <div class="feature-text">
                        <div class="feature-title">Древовидная структура</div>
                        <div class="feature-description">Организуйте заметки в виде связанного дерева мыслей</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">🔗</div>
                    <div class="feature-text">
                        <div class="feature-title">Связи между идеями</div>
                        <div class="feature-description">Создавайте связи между заметками для лучшего понимания</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">💡</div>
                    <div class="feature-text">
                        <div class="feature-title">Умная организация</div>
                        <div class="feature-description">Находите важное быстро благодаря структурированному подходу</div>
                    </div>
                </div>
            </div>

            <div class="button-container">
                <a href="{dashboard_url}" class="start-button">Начать работу</a>
            </div>
        </div>

        <div class="footer">
            <div class="footer-logo">Brain Notes</div>
            <div>Организуйте свои мысли. Создавайте связи. Развивайтесь.</div>
        </div>
    </div>
</body>
</html>
'''