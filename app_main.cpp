#include <QCoreApplication>
#include <QThreadPool>
#include <QRunnable>
#include <QString>
#include <QStringList>
#include "config.h"
#include <stdint.h>
//My includes
#include "spdlog/spdlog.h"
using namespace spdlog;

auto logger = spdlog::stdout_color_mt("logger");

class task : public QRunnable
{
    void run()
    {
        qDebug() << "Hello world from thread" << QThread::currentThread();
    }
}

int main(int argc, char** argv)
{
	QCoreApplication a(argc, argv);
	QCoreApplication::setApplicationName(PROGRAM_NAME);
    QCoreApplication::setApplicationVersion(PROGRAM_VERSION);
	QCommandLineParser parser;
    parser.setApplicationDescription(PROGRAM_DESCRIPTION);
    parser.addHelpOption();
    parser.addVersionOption();
	QThreadPool tp;
	QCommandLineOption thread_count_option(QStringList() << "t" << "threads",
            QCoreApplication::translate("main", QCoreApplication::translate("Max count of threads to work. Default is "+QString(tp->maxThreadCount())+".")),
            QCoreApplication::translate("main", "threads"));
    parser.addOption(thread_count_option);
	QCommandLineOption loglevel_option(QStringList() << "l" << "loglevel",
            QCoreApplication::translate("main", QCoreApplication::translate("Loglevel of the program. It can be error/warning/info/debug")),
            QCoreApplication::translate("main", "loglevel"));
    parser.addOption(loglevel_option);
	//My options
	parser.process(app);
	const QStringList args = parser.positionalArguments();
	int32_t thread_count = parser.value(thread_count_option).toInt();
	QString loglevel = parser.value(loglevel_option);
	if(loglevel=="error")
	{
    	spdlog::set_level(spdlog::level::error);
	}
	else if(loglevel=="warning")
	{
    	spdlog::set_level(spdlog::level::warning);
	}
	else if(loglevel=="info")
	{
    	spdlog::set_level(spdlog::level::info);
	}
	else if(loglevel=="debug")
	{
    	spdlog::set_level(spdlog::level::debug);
	}
	//My parse
	setMaxThreadCount(thread_count);
	tp.start(task);
	return a.exec();
}
