def verify_email_template(verify_url: str) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <table width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
          <tr>
            <td style="background-color: #1f2937; color: #ffffff; padding: 16px 24px; font-size: 20px; font-weight: bold;">
              CRM Service Center
            </td>
          </tr>
          <tr>
            <td style="padding: 24px;">
              <p style="font-size: 16px; margin-bottom: 16px;">
                Добро пожаловать в CRM Service Center!
              </p>
              <p style="font-size: 14px; margin-bottom: 16px;">
                Для завершения регистрации подтвердите, пожалуйста, ваш email.
              </p>
              <p style="text-align: center; margin: 24px 0;">
                <a href="{verify_url}"
                   style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 14px;">
                  Подтвердить email
                </a>
              </p>
              <p style="font-size: 12px; color: #6b7280; margin-top: 24px;">
                Если кнопка не работает, скопируйте и вставьте эту ссылку в адресную строку браузера:
              </p>
              <p style="font-size: 12px; color: #374151; word-break: break-all;">
                {verify_url}
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f3f4f6; padding: 12px 24px; font-size: 12px; color: #6b7280; text-align: center;">
              Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
