#include <QCoreApplication>
#include <QThreadPool>
#include <QRunnable>
#include <QString>
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
    spdlog::set_level(spdlog::level::debug);
    logger->debug("{0}: {1} [thread %t] - Enter in function {2}", __FILE__, __LINE__, __FUNCTION__);
	QCoreApplication a(argc, argv);
	QCoreApplication::setApplicationName(PROGRAM_NAME);
    QCoreApplication::setApplicationVersion(PROGRAM_VERSION);
	QCommandLineParser parser;
    parser.setApplicationDescription(PROGRAM_DESCRIPTION);
    parser.addHelpOption();
    parser.addVersionOption();
	QThreadPool tp;
	QCommandLineOption thread_count_option(QStringList() << "t" << "threads",
            QCoreApplication::translate("main", "Max count of threads to work. Default is "+QString(tp->maxThreadCount())+"."),
            QCoreApplication::translate("main", "threads"));
    parser.addOption(targetDirectoryOption);
	//My options
	parser.process(app);
	const QStringList args = parser.positionalArguments();
	int thread_count = parser.value(thread_count_option).toInt();
	//My parse
	setMaxThreadCount(thread_count);
	tp.start(task);
	return a.exec();
}
